#!/usr/bin/env python

import argparse
import sys
from typing import Dict, List, Optional
import yaml


def parse_labels(raw: Optional[str]) -> Optional[Dict[str, str]]:
    if not raw:
        return None
    labels: Dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"Invalid label format: '{pair}' (expected key=value)")
        k, v = pair.split("=", 1)
        labels[k.strip()] = v.strip()
    return labels or None


def parse_envs(raw: Optional[str]) -> Optional[List[Dict[str, str]]]:
    if not raw:
        return None
    envs: List[Dict[str, str]] = []
    for pair in raw.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"Invalid environment variable format: '{pair}' (expected KEY=VALUE)")
        k, v = pair.split("=", 1)
        envs.append({"name": k.strip(), "value": v.strip()})
    return envs or None


def build_deployment_manifest(
    name: str,
    labels: Optional[Dict[str, str]] = None,
    replicas: Optional[int] = None,
    envs: Optional[List[Dict[str, str]]] = None,
) -> Dict:
    if replicas is None or replicas == '':
        replicas = 3

    deployment: Dict = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": {
                    "app": name,
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": name,
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": "nginx:latest",
                        }
                    ]
                },
            },
        },
    }

    if labels:
        deployment["metadata"]["labels"] = labels
        deployment["spec"]["template"]["metadata"]["labels"].update(labels)

    if envs:
        deployment["spec"]["template"]["spec"]["containers"][0]["env"] = envs

    return deployment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Kubernetes Deployment manifest generator")
    parser.add_argument(
        "--name", required=True,
        help="Name of the Deployment and container"
    )
    parser.add_argument(
        "--labels",
        required=False,
        help="Labels in the format key1=value1,key2=value2",
    )
    parser.add_argument(
        "--replicas",
        required=False,
        help="Number of replicas (defaults to 3 if not provided)",
    )
    parser.add_argument(
        "--envs",
        required=False,
        help="Environment variables in the format KEY1=VALUE1;KEY2=VALUE2",
    )

    args = parser.parse_args(argv)

    try:
        labels = parse_labels(args.labels)
        envs = parse_envs(args.envs)
    except ValueError as e:
        print(f"Parameter parsing error: {e}", file=sys.stderr)
        return 1

    deployment = build_deployment_manifest(
        name=args.name,
        labels=labels,
        replicas=args.replicas,
        envs=envs,
    )

    with open("deployment.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(deployment, f, sort_keys=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
