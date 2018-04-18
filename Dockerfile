FROM ubuntu:16.04

# FROM ubuntu:14.04
# FROM debian

MAINTAINER dan farmer zen@trouble.org

# some things I use for OOB/sys investigations
RUN apt-get update &&     \
    apt-get -y install    \
    ca-certificates       \
    binutils              \
    freeipmi              \
    ipmitool              \
    strace                \
    wget                  \
    wsmancli &&           \
    update-ca-certificates    

CMD [ "wsman" ]

