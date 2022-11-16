ARG REL_TAG=latest
FROM openeuler/openeuler:$REL_TAG
RUN dnf in shadow passwd sudo tar -y && dnf clean all && rm -rf /var/cache/dnf 
RUN sed -i '/TMOUT=300/d' /etc/bashrc
