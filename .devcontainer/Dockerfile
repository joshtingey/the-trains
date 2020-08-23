FROM ubuntu:20.04

# Options
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="false"
ARG ENABLE_NONROOT_DOCKER="true"
ARG SOURCE_SOCKET=/var/run/docker-host.sock
ARG TARGET_SOCKET=/var/run/docker.sock
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install needed packages and setup non-root user.
COPY .devcontainer/library-scripts/*.sh /tmp/library-scripts/
RUN apt-get update \
    && /bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" \
    # Use Docker script from script library to set things up
    && /bin/bash /tmp/library-scripts/docker-debian.sh "${ENABLE_NONROOT_DOCKER}" "${SOURCE_SOCKET}" "${TARGET_SOCKET}" "${USERNAME}" \
    # Clean up
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts/

# Setup KUBECONFIG file
COPY .devcontainer/copy-kube-config.sh /usr/local/share/
RUN echo "source /usr/local/share/copy-kube-config.sh" | tee -a /root/.bashrc >> /root/.zshrc

# Install kubectl
RUN curl -sSL -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl

# Install skaffold
RUN curl -Lo skaffold https://storage.googleapis.com/skaffold/builds/latest/skaffold-linux-amd64 \
    && mv skaffold /usr/local/bin/skaffold && chmod +x /usr/local/bin/skaffold

# Install pip requirements
COPY src/requirements.txt /tmp/pip-tmp/requirements_0.txt
COPY src/common/requirements.txt /tmp/pip-tmp/requirements_1.txt
COPY src/collector/requirements.txt /tmp/pip-tmp/requirements_2.txt
COPY src/generator/requirements.txt /tmp/pip-tmp/requirements_3.txt
COPY src/dash/requirements.txt /tmp/pip-tmp/requirements_4.txt
RUN pip3 --disable-pip-version-check --no-cache-dir install \
    -r /tmp/pip-tmp/requirements_0.txt \
    -r /tmp/pip-tmp/requirements_1.txt \
    -r /tmp/pip-tmp/requirements_2.txt \
    -r /tmp/pip-tmp/requirements_3.txt \
    -r /tmp/pip-tmp/requirements_4.txt \
    && rm -rf /tmp/pip-tmp

# Add to PYTHONPATH
RUN echo "export PYTHONPATH=$PYTHONPATH:/workspaces/the-trains" | tee -a /root/.bashrc >> /root/.zshrc
RUN echo "export PYTHONPATH=$PYTHONPATH:/workspaces/the-trains/src" | tee -a /root/.bashrc >> /root/.zshrc

# Setting the ENTRYPOINT to docker-init.sh will configure non-root access to 
# the Docker socket if "overrideCommand": false is set in devcontainer.json. 
# The script will also execute CMD if you need to alter startup behaviors.
ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]