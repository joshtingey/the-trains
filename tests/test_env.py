import os


def test_k8s_server():
    assert os.getenv('K8S_SERVER') is not None


def test_k8s_certificate():
    assert os.getenv('K8S_CERTIFICATE') is not None


def test_k8s_token():
    assert os.getenv('K8S_TOKEN') is not None
