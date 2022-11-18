ARG REL_TAG=latest
FROM openeuler/openeuler:$REL_TAG
RUN dnf groupinstall core -y -x kernel* -x tune* -x grub2* && dnf clean all && rm -rf /var/cache/dnf 
RUN sed -i '/TMOUT=300/d' /etc/bashrc
