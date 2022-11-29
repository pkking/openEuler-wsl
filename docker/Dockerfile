ARG REL_TAG=latest
FROM openeuler/openeuler:$REL_TAG
RUN dnf groupinstall core -y  && dnf install bc -y && dnf clean all && rm -rf /var/cache/dnf
COPY wsl.conf /etc/wsl.conf
RUN sed -i '/TMOUT=300/d' /etc/bashrc
