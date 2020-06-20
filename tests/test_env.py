import os


def test_cert_email():
    assert os.getenv("CERT_EMAIL") is not None


def test_domain():
    assert os.getenv("DOMAIN") is not None


def test_mongo_user():
    assert os.getenv("MONGO_INITDB_ROOT_USERNAME") is not None


def test_mongo_pass():
    assert os.getenv("MONGO_INITDB_ROOT_PASSWORD") is not None


def test_k8s_server():
    assert os.getenv("K8S_SERVER") is not None


def test_k8s_certificate():
    assert os.getenv("K8S_CERTIFICATE") is not None


def test_k8s_token():
    assert os.getenv("K8S_TOKEN") is not None
