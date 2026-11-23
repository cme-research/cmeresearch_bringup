"""Static consistency checks for cmeresearch_bringup launch files and configs.

Pure file analysis (yaml + ast), so it needs no other cme packages at test time.

Known, not-yet-fixed problems are listed in KNOWN_BROKEN_* and marked as strict
xfail: CI stays green and documents them, any *new* breakage fails CI, and
fixing a known one makes the xfail "unexpectedly pass" so the list gets cleaned up.
"""

import ast
import math
import pathlib
import re
from collections import defaultdict

import pytest
import yaml

PKG = 'cmeresearch_bringup'
ROOT = pathlib.Path(__file__).resolve().parent.parent
LAUNCH_PY = sorted(
    p for d in ('launch', 'driver', 'simulation') for p in (ROOT / d).glob('*.launch.py'))
YAML_FILES = sorted(
    p for d in ('config', 'simulation') for ext in ('*.yaml', '*.yml')
    for p in (ROOT / d).rglob(ext))
ROBOTS_WITH_TWIST_MUX = ('cmexa', 'cmexaiii', 'cmexamini')

# Launch file -> config path (relative to the package share dir) that it loads
# but that is missing from the source tree or the CMake install rules.
KNOWN_BROKEN_REFERENCES = {
    ('driver/joy2twist.launch.py', 'config/cmexa/joy2twist.yaml'):
        'file does not exist (only joy2twist_ugv.yaml)',
    ('launch/cmexa_omni.launch.py', 'config/cmexa/base_mecanum_controllers.yaml'):
        'file is named cmexa_base_mecanum_controllers.yaml',
    ('launch/cmexa_omni_navi_mapping.launch.py', 'config/cmexa/base_mecanum_controllers.yaml'):
        'file is named cmexa_base_mecanum_controllers.yaml',
}
# Launch files present in the repo but not installed by CMakeLists.txt.
KNOWN_UNINSTALLED_LAUNCH = {
    'launch/unico_mini.launch.py': 'legacy Unico Mini launch file',
    'launch/unico_mini_omni.launch.py': 'legacy Unico Mini launch file',
}


def rel(p):
    return p.relative_to(ROOT).as_posix()


# --- CMake install rules -------------------------------------------------------

def installed_files():
    """Map installed path (relative to share/<pkg>) -> source path."""
    cmake = (ROOT / 'CMakeLists.txt').read_text()
    cmake = re.sub(r'#.*', '', cmake)
    out = {}
    for files, dest in re.findall(
            r'install\s*\(\s*FILES(.*?)DESTINATION\s+share/\$\{PROJECT_NAME\}/?(\S*)\s*\)',
            cmake, re.S):
        for src in files.split():
            out[(pathlib.PurePosixPath(dest) / pathlib.PurePosixPath(src).name).as_posix()] = src
    return out


INSTALLED = installed_files()


def test_install_rules_reference_existing_files():
    missing = sorted(src for src in INSTALLED.values() if not (ROOT / src).exists())
    assert not missing, f'CMakeLists.txt installs files that do not exist: {missing}'


# --- YAML ---------------------------------------------------------------------

@pytest.mark.parametrize('path', YAML_FILES, ids=rel)
def test_yaml_parses(path):
    yaml.safe_load(path.read_text())


# --- launch files ---------------------------------------------------------------

def parse(path):
    return ast.parse(path.read_text(), filename=str(path))


@pytest.mark.parametrize('path', LAUNCH_PY, ids=rel)
def test_launch_file_defines_generate_launch_description(path):
    tree = parse(path)
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert 'generate_launch_description' in names


def call_name(node):
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, 'id', None)


def literal_path(parts):
    """Join path parts if they are all literals rooted at this package's share dir."""
    if not parts:
        return None
    head, rest = parts[0], parts[1:]
    if not (isinstance(head, ast.Call)
            and call_name(head) in ('FindPackageShare', 'get_package_share_directory')
            and head.args and isinstance(head.args[0], ast.Constant)
            and head.args[0].value == PKG):
        return None
    strs = []
    for part in rest:
        if not (isinstance(part, ast.Constant) and isinstance(part.value, str)):
            return None  # built from a launch argument / substitution
        strs.append(part.value.strip('/'))
    path = '/'.join(s for s in strs if s)
    return path if '.' in pathlib.PurePosixPath(path).name else None


def referenced_configs(path):
    refs = set()
    for node in ast.walk(parse(path)):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name == 'PathJoinSubstitution' and node.args and isinstance(node.args[0], ast.List):
            p = literal_path(node.args[0].elts)
        elif name == 'join':  # os.path.join
            p = literal_path(node.args)
        else:
            continue
        if p:
            refs.add(p)
    return refs


REFERENCES = sorted((rel(lf), ref) for lf in LAUNCH_PY for ref in referenced_configs(lf))


def test_reference_extraction_finds_configs():
    assert len(REFERENCES) >= 10, 'static launch-file analysis stopped finding config paths'


def _ref_param(launch_file, ref):
    reason = KNOWN_BROKEN_REFERENCES.get((launch_file, ref))
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(launch_file, ref, id=f'{launch_file}:{ref}', marks=marks)


@pytest.mark.parametrize(
    'launch_file,ref', [_ref_param(lf, r) for lf, r in REFERENCES])
def test_referenced_config_exists_and_is_installed(launch_file, ref):
    assert ref in INSTALLED, f'{launch_file} loads {ref}, which CMakeLists.txt does not install'
    assert (ROOT / INSTALLED[ref]).exists(), f'{INSTALLED[ref]} does not exist'


def test_known_broken_list_is_current():
    stale = sorted(set(KNOWN_BROKEN_REFERENCES) - set(REFERENCES))
    assert not stale, f'KNOWN_BROKEN_REFERENCES entries no longer referenced: {stale}'


@pytest.mark.parametrize('path', [
    pytest.param(p, id=rel(p), marks=[pytest.mark.xfail(
        strict=True, reason=KNOWN_UNINSTALLED_LAUNCH[rel(p)])]
        if rel(p) in KNOWN_UNINSTALLED_LAUNCH else [])
    for p in LAUNCH_PY if rel(p).startswith('launch/')])
def test_launch_file_is_installed(path):
    assert f'launch/{path.name}' in INSTALLED


# --- twist_mux ------------------------------------------------------------------

EXPECTED_PRIORITY_ORDER = ['joystick', 'keyboard', 'mqtt', 'navigation']


@pytest.mark.parametrize('robot', ROBOTS_WITH_TWIST_MUX)
def test_twist_mux_priorities(robot):
    data = yaml.safe_load((ROOT / 'config' / robot / 'twist_mux_topics.yaml').read_text())
    topics = data['twist_mux']['ros__parameters']['topics']
    assert set(EXPECTED_PRIORITY_ORDER) <= set(topics), f'missing inputs in {robot}'
    prios = [topics[name]['priority'] for name in EXPECTED_PRIORITY_ORDER]
    # Documented order: joystick 100 > keyboard 90 > MQTT 80 > Nav2 10.
    assert prios == sorted(prios, reverse=True) and len(set(prios)) == len(prios), prios
    assert topics['joystick']['topic'] == '/teleop/cmd_vel'
    assert topics['mqtt']['topic'] == '/mqtt/cmd_vel'
    for name, t in topics.items():
        assert 0 <= t['priority'] <= 255, name
        assert t['timeout'] > 0, name
    assert len({t['topic'] for t in topics.values()}) == len(topics), 'duplicate input topic'


# --- stepper driver nodes ---------------------------------------------------------

def kwarg(call, name):
    return next((k.value for k in call.keywords if k.arg == name), None)


def literal_items(dict_node):
    out = {}
    for k, v in zip(dict_node.keys, dict_node.values):
        try:
            out[ast.literal_eval(k)] = ast.literal_eval(v)
        except ValueError:
            pass  # value comes from a launch substitution
    return out


def stepper_nodes(path):
    nodes = []
    for node in ast.walk(parse(path)):
        if not (isinstance(node, ast.Call) and call_name(node) == 'Node'):
            continue
        exe = kwarg(node, 'executable')
        if not (isinstance(exe, ast.Constant) and exe.value == 'stepper_driver_node'):
            continue
        params = {}
        p = kwarg(node, 'parameters')
        if isinstance(p, ast.List):
            for d in p.elts:
                if isinstance(d, ast.Dict):
                    params.update(literal_items(d))
        remaps = {}
        r = kwarg(node, 'remappings')
        if isinstance(r, ast.List):
            for t in r.elts:
                try:
                    a, b = ast.literal_eval(t)
                    remaps[a] = b
                except ValueError:
                    pass
        nodes.append((node.lineno, params, remaps))
    return nodes


STEPPER_LAUNCH = [p for p in LAUNCH_PY if stepper_nodes(p)]


def test_stepper_launch_files_found():
    assert STEPPER_LAUNCH, 'no launch file starts stepper_driver_node'


@pytest.mark.parametrize('path', STEPPER_LAUNCH, ids=rel)
def test_stepper_node_parameters(path):
    ports = defaultdict(list)
    wheels = []
    for line, params, remaps in stepper_nodes(path):
        where = f'{rel(path)}:{line}'
        res = params.get('step_resolution', 8)
        assert res in [2 ** i for i in range(9)], f'{where}: invalid step_resolution {res}'
        pos = str(params.get('brick_position', 'a'))
        assert re.fullmatch(r'[a-hA-H]', pos), f'{where}: invalid brick_position {pos!r}'
        ports[(params.get('bricklet_host', 'localhost'), pos.lower())].append(where)
        assert params.get('gear_ratio', 1.0) > 0, where
        assert params.get('steps_per_revolution', 200) > 0, where
        assert params.get('max_step_vel', 1000) > 0, where
        assert 0 <= params.get('freewheel_mode', 0) <= 3, where
        wheel = params.get('wheel_name')
        wheels.append(wheel)
        if wheel and {'drive_input', 'drive_output'} <= set(remaps):
            prefix = wheel.removesuffix('_wheel')
            for key in ('drive_input', 'drive_output'):
                assert f'/{prefix}/' in remaps[key], (
                    f'{where}: wheel {wheel} remaps {key} to {remaps[key]}')
            assert remaps['drive_input'].endswith('/cmd_vel'), where
            assert remaps['drive_output'].endswith('/feedback'), where
    dup_ports = {k: v for k, v in ports.items() if len(v) > 1}
    assert not dup_ports, f'two drivers on the same bricklet port: {dup_ports}'
    named = [w for w in wheels if w]
    assert len(named) == len(set(named)), f'duplicate wheel_name: {wheels}'


@pytest.mark.parametrize('path', STEPPER_LAUNCH, ids=rel)
def test_stepper_nodes_respawn(path):
    """A dead wheel driver must come back on its own (nothing else restarts it)."""
    for node in ast.walk(parse(path)):
        if not (isinstance(node, ast.Call) and call_name(node) == 'Node'):
            continue
        exe = kwarg(node, 'executable')
        if not (isinstance(exe, ast.Constant) and exe.value == 'stepper_driver_node'):
            continue
        respawn = kwarg(node, 'respawn')
        assert isinstance(respawn, ast.Constant) and respawn.value is True, (
            f'{rel(path)}:{node.lineno}: stepper_driver_node without respawn=True')


@pytest.mark.parametrize('path', STEPPER_LAUNCH, ids=rel)
def test_stepper_nodes_share_drive_geometry(path):
    """All wheels of one robot should use the same step/gear configuration."""
    keys = ('step_resolution', 'steps_per_revolution', 'gear_ratio', 'max_step_vel')
    configs = {tuple(params.get(k) for k in keys) for _, params, _ in stepper_nodes(path)}
    assert len(configs) == 1, f'{rel(path)}: wheels differ in {keys}: {configs}'


# --- controllers ------------------------------------------------------------------

@pytest.mark.parametrize('path', sorted((ROOT / 'config').rglob('*controllers.yaml')), ids=rel)
def test_controller_yaml_shape(path):
    data = yaml.safe_load(path.read_text())
    cm = data.get('controller_manager', {}).get('ros__parameters', {})
    assert cm.get('update_rate', 0) > 0, 'controller_manager.update_rate must be > 0'
    declared = {k for k, v in cm.items() if isinstance(v, dict) and 'type' in v}
    assert declared, 'no controllers declared'
    for name in declared:
        if name == 'joint_state_broadcaster':
            continue
        assert name in data and 'ros__parameters' in data[name], (
            f'controller {name} declared without a parameter section')
        params = data[name]['ros__parameters']
        for key, val in params.items():
            if key.startswith('wheel') and isinstance(val, (int, float)):
                assert math.isfinite(val) and val > 0, f'{name}.{key} = {val}'
