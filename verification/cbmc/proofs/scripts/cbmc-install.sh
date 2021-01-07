#!/bin/bash

CBMCGIT='/tmp/git'
CBMCBIN='/tmp/cbmc'
BINDIRS="${CBMCGIT}/cbmc/src/goto-analyzer/goto-analyzer
	${CBMCGIT}/cbmc/src/goto-cc/goto-cc
	${CBMCGIT}/cbmc/src/goto-instrument/goto-instrument
	${CBMCGIT}/cbmc/src/goto-diff/goto-diff
	${CBMCGIT}/cbmc/src/cbmc/cbmc"
USRBINPATH='/usr/bin'

function git_clone {
    if [ -d ${CBMCGIT} ] 
    then
        echo "Directory ${CBMCGIT} DOES exists." 
        return
    fi
    mkdir -p ${CBMCGIT}; \
	cd ${CBMCGIT}; \
	git clone https://github.com/diffblue/cbmc.git; \
    cd ${CBMCGIT}/cbmc; \
	git checkout develop;
}

function cmake_cbmc {
    if [ -d ${CBMCGIT} ] 
    then
        echo "Directory ${CBMCGIT} DOES exists." 
        return
    fi
    make DOWNLOADER='wget' -C ${CBMCGIT}/cbmc/src minisat2-download
    make -C ${CBMCGIT}/cbmc/src CXX=g++ -j8
}

function cbmc_cp_bin_into_path {
    mkdir -p ${CBMCBIN}
    for bin in ${BINDIRS}; do
        echo ${bin}
        cp ${bin} ${USRBINPATH}
    done
}

function pre_pkgs_install_ckecking {
    echo "Starting installing pre-requsite pkgs";
    apt-get update -y;
    for i in gcc g++ flex bison make git libwww-perl patch ccache libc6-dev-i386 jq cmake; do
        command -v "$i" >/dev/null 2>&1 || {
            echo >&2 "Command $i required in \$PATH";
            apt-get install -y $i;
        }
    done
}

COMMANDS_IN_PATH=true
for i in cbmc goto-cc goto-instrument; do
    command -v "$i" >/dev/null 2>&1 || {
        echo >&2 "Command $i required in \$PATH";
        COMMANDS_IN_PATH=false;
    }
done
if [ "$COMMANDS_IN_PATH" = false ]; then
    pre_pkgs_install_ckecking;
    echo "Starting installing cbmc"
    git_clone;
    cmake_cbmc;
    cbmc_cp_bin_into_path;
    echo "Installed cbmc...DONE!"
fi
