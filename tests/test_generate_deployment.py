import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scripts.generate_deployment_manifest import build_deployment_manifest


def test_default_replicas():
    dep = build_deployment_manifest(name="my-app")
    assert dep["spec"]["replicas"] == 3


def test_no_labels_when_none():
    dep = build_deployment_manifest(name="my-app")
    assert "labels" not in dep["metadata"]


def test_envs_added():
    envs = [{"name": "FOO", "value": "bar"}]
    dep = build_deployment_manifest(name="my-app", envs=envs)
    c0 = dep["spec"]["template"]["spec"]["containers"][0]
    assert c0["env"] == envs