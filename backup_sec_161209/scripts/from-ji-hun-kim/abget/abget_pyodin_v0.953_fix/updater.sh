#!/bin/bash
##
#  Copyright (C) 2015, Samsung Electronics, Co., Ltd. All Rights Reserved.
#  Written by System S/W Group, S/W Platform R&D Team,
#  Mobile Communication Division.
##

##
# Project Name : Auto Update Script
#
# Project Description :
#
# Comments : tabstop = 8, shiftwidth = 8 noexpandtab
##

##
# File Name : updater.sh
#
# File Description :
#  Auto Update Script
#
# Author : Taehyo Song(taehyo.song@samsung.com)
# Dept : System S/W R&D Team Grp.2
# Created Date : 17-Jun-2015
# Last Update: 17-Jun-2015
# Version : 0.8
##

VERSION="0.8"
VERSION_INFO=".version_info"
UPDATE_INFO=".update_info"

SUPPORTED_VERSION="3.200"

WITHOUT_USER_CONFIRM=false
CHECK_UPDATE_MODE=false
PROCEED_UPDATE_MODE=false

NEED_RESTORE=false
UPDATE_DATE=`date +%Y%m%d.%H%M%S`
BACKUP_FILE="backup_${UPDATE_DATE}.tar.bz2"

PROTOCOL="http://"
IP_ADDR="10.252.81.137"
BASE_ADDR="~bjun.mun/release/pyodin"
UPDATE_SERVER="${PROTOCOL}${IP_ADDR}/${BASE_ADDR}"

SCRIPT_DIR=$(dirname $0)
DOWNLOAD_DIR="__abget_download"

UPDATE_LIST=()
CHANGED_LIST=()

DEBUG=1
VERBOSE=2
INFO=3
WARNING=4
ERROR=100

DEBUG_LEVEL=${INFO}

function print_msg() {
	[ ${1} -ge ${DEBUG_LEVEL} ] && printf "${2}"
}

function pr_debug() {
	print_msg ${DEBUG} "${1}"
}

function pr_info() {
	print_msg ${INFO} "${1}"
}

function pr_verbose() {
	print_msg ${VERBOSE} "${1}"
}

function pr_warning() {
	print_msg ${WARNING} "${1}"
}

function pr_error() {
	print_msg ${ERROR} "${1}"
}

function exit_on_error() {
	if [ "$1" -ne 0 ]; then
		pr_error "\nError: $2 exit with $1\n"

		[ ${NEED_RESTORE} = true ] && restore_data
		remove_temp_files

		pr_error "\n"

	        exit 1
	fi
}

function build_environment() {
	TEMP_DIR=${TMPDIR}
	[ "${TEMP_DIR}x" = "x" ] && TEMP_DIR="/tmp"

	SCRIPT_DIR=$(get_abs_path ${SCRIPT_DIR})
}

function remove_if_containing_element() {
	local __el
	local __idx=0

	for __el in "${UPDATE_LIST[@]}"; do
		if [ "${__el}" == "${1}" ]; then
			unset UPDATE_LIST[${__idx}]
			return
		fi
		__idx=`expr ${__idx} + 1`
	done
}

function get_abs_path() {
	local __path=${1}

	[ ${__path:0:1} = "~" ] && __path=${HOME}${__path:1}
	[ ! -d ${__path} ] && return
	echo `eval cd ${__path};pwd`
}

function get_filename() {
	local __file=${1}
	local __filename=${__file%.*}
	echo ${__filename}
}

function get_extension() {
	local __file=${1}
	local __extension=${__file##*.}
	echo ${__extension}
}

function get_filename_without_path {
	echo $(basename "${1}")	# Get file name witout path
}

function get_variable() {
	echo $(echo "${1}" \
		| grep "${2}" \
		| cut -d "=" -f 2 \
		| sed -e 's/^ *//g' -e 's/ *$//g')
}

function check_server() {
	pr_verbose "Checking update server..."
	eval "ping -c 1 ${IP_ADDR} > /dev/null"
	exit_on_error $? "Can't connect to server."
	pr_verbose " done\n"
}

function check_update_info() {
	local __version_info="${SCRIPT_DIR}/${VERSION_INFO}"
	local __need_update=0

	pr_warning "Checking update..."

	[ ! -f ${__version_info} ] && exit_on_error -1 "Can't find version information."

	CURRENT_VERSION=$(cat ${__version_info})

	pushd $(pwd) > /dev/null
	cd ${TEMP_DIR}

	eval "rm -f ${VERSION_INFO}"
	eval "wget --no-cache -q ${UPDATE_SERVER}/${VERSION_INFO}"
	exit_on_error $? "Failed to get version information from server."

	UPDATED_VERSION=$(cat ${VERSION_INFO})

	pr_warning " done\n"
	__need_update=$(bc <<< "${CURRENT_VERSION:0:5} < ${UPDATED_VERSION:0:5}")
	if [ "${__need_update}" != 1 ]; then
		pr_warning "Pyodin(Ver.${CURRENT_VERSION}) is latest version.\n"
		exit 0
	fi
	popd > /dev/null
}

function user_confirm() {
	local __ans

	[ ${WITHOUT_USER_CONFIRM} = true ] && return

	pr_error "New Pyodin(Ver.${UPDATED_VERSION}) is available.\n"
	pr_error "Type 'y' to proceed update "
	read -n1 -p "[y/N] "  __ans

	pr_error "\n\n"
	if [[ "${__ans}" != "y" && "${__ans}" != "Y" ]]; then
		pr_error "Update aborted.\n\n"
		exit 0
	fi
}

function check_update() {
	check_server
	check_update_info
	user_confirm
}

function build_update_list() {
	local __found=false

	pr_verbose "  Building update list...\n"

	UPDATE_LIST=()
	pushd $(pwd) > /dev/null
	cd ${TEMP_DIR}

	eval "rm -f ${UPDATE_INFO}"
	eval "wget --no-cache -q ${UPDATE_SERVER}/${UPDATE_INFO}"
	exit_on_error $? "Failed to get update information from server."

	while read line; do
		if [ ${__found} = false ]; then
			__line=$(get_variable "${line}" "VERSION")
			[ "${__line}" == "${CURRENT_VERSION}" ] && __found=true
		else
			__line=($(get_variable "${line}" "FILES"))

			for __item in ${__line[@]}; do
				remove_if_containing_element "${__item}"
				UPDATE_LIST+=(${__item})
			done
		fi
	done < ${UPDATE_INFO}

	eval "rm -f ${UPDATE_INFO}"

	[ ${__found} = false ] && exit_on_error -1 "Failed to get updated file list."

	popd > /dev/null
}

function apply_patch() {
	local __patch=${1}
	pr_verbose "    Applying patch: ${__patch}\n"

	eval "cp -f ${__patch} ${SCRIPT_DIR}"
	exit_on_error $? "Failed to copy patch(${__patch}}"

	pushd $(pwd) > /dev/null
	cd ${SCRIPT_DIR}

	eval "patch -p1 -s -f < ${__patch}"
	__res=$?
	eval "rm -f ${__patch}"
	exit_on_error ${__res} "Failed to apply patch(${__patch}}"

	popd > /dev/null
}

function download_update_files() {
	local __res=
	local __download_dir="${TEMP_DIR}/${DOWNLOAD_DIR}"

	pr_info "  Downloading files...\n"
	pushd $(pwd) > /dev/null
	cd ${TEMP_DIR}

	[ -d ${__download_dir} ] && eval "rm -rf ${__download_dir}" 

	eval "mkdir ${DOWNLOAD_DIR}"
	exit_on_error $? "Failed to create tmp directory(${DOWNLOAD_DIR}}"

	for __list in ${UPDATE_LIST[@]}; do
		cd ${__download_dir}

		local __dir=$(dirname ${__list})
		local __file=$(basename ${__list})

		if [[ "${__dir}x" != "x" && "${__dir}" != "." ]]; then
			eval "mkdir -p ${__dir}"
			exit_on_error $? "Failed to create directory(${__dir})"

			cd ${__dir}
		fi

		if [ "${__file: -1}" != "/" ]; then
			pr_verbose "    => ${__list}... "
			eval "wget --no-cache -q ${UPDATE_SERVER}/${__list}"
			__res=$?
			if [ ${__res} -ne 0 ]; then
				pr_verbose "[fail]\n"
				exit_on_error ${__res} "Failed to download file(${__file})"
			fi
			pr_verbose "[done]\n"
		fi
	done

	pr_verbose "\n"
	popd > /dev/null
}

function backup_data() {
	local __backup_list=()

	pr_verbose "  Backing-up files...\n"

	pushd $(pwd) > /dev/null
	cd ${SCRIPT_DIR}

	for __list in ${UPDATE_LIST[@]}; do
		local __dir=$(dirname ${__list})
		local __file=$(basename ${__list})

		if [ -f ${__list} ]; then
			__backup_list+=(${__list})
		fi
	done

	if [ ${#__backup_list[@]} != 0 ]; then
		eval "tar cjf ${BACKUP_FILE} ${__backup_list[@]}"
		exit_on_error $? "Failed to create bakcup data."
	fi

	popd > /dev/null
}

function restore_data() {
	pr_info "Restore files... "

	pushd $(pwd) > /dev/null
	cd ${SCRIPT_DIR}

	for __list in ${CHANGED_LIST[@]}; do
		eval "rm -rf ${__list}"
	done

	if [ -f ${BACKUP_FILE} ]; then
		eval "tar xjf ${BACKUP_FILE}"
		exit_on_error $? "Failed to restore data."
	fi

	pr_info "done\n"
	popd > /dev/null
}

function remove_temp_files() {
	local __download_dir="${TEMP_DIR}/${DOWNLOAD_DIR}"
	local __backup_file="${SCRIPT_DIR}/${BACKUP_FILE}"

	[ -f ${__backup_file} ] && eval "rm -f ${__backup_file}"
	[ -d ${__download_dir} ] && eval "rm -rf ${__download_dir}"
}

function apply_updates() {
	local __download_dir="${TEMP_DIR}/${DOWNLOAD_DIR}"

	pr_info "  Applying updates...\n"

	pushd $(pwd) > /dev/null
	cd ${__download_dir}

	NEED_RESTORE=true
	for __list in ${UPDATE_LIST[@]}; do
		local __dir=$(dirname ${__list})
		local __file=$(basename ${__list})

		CHANGED_LIST+=(${__list})
		if [ "$(get_extension ${__file})" = "patch" ]; then
			apply_patch ${__file}
		else
			if [[ "${__dir}x" != "x" && "${__dir}" != "." ]]; then
				eval "mkdir -p ${SCRIPT_DIR}/${__dir}"
				exit_on_error $? "Failed to create directory(${__dir})"
			fi

			if [ "${__list: -1}" != "/" ]; then
				pr_verbose "    Copying File: ${__file}\n"
				eval "cp -f ${__list} ${SCRIPT_DIR}/${__list}"
				exit_on_error $? "Failed to copy file(${__file})"
			else
				eval "mkdir -p ${SCRIPT_DIR}/${__list}"
				exit_on_error $? "Failed to create directory(${__dir})"
			fi
		fi
	done

	eval "echo \"${UPDATED_VERSION}\" > ${SCRIPT_DIR}/${VERSION_INFO}"
	popd > /dev/null

	pr_verbose "\n"
}

function proceed_update() {
	pr_warning "Updating...\n"

	build_update_list
	download_update_files
	backup_data
	apply_updates
	remove_temp_files

	pr_warning "done\n\n"
	pr_warning "Update Complete. (Ver.${UPDATED_VERSION})\n\n"
}

function version() {
	printf "Auto Updater Ver.${VERSION}\n"
	printf "Taehyo Song(taehyo.song@samsung.net)\n\n"

	exit 0
}

function usage() {
	local __executor=$(get_filename_without_path ${0})

	echo "Usage: ${__executor} <options>..."
	echo "      -s, --silent           no verbose message"
	echo "      -f, --force            proceed updatewithout user confirm"
	echo "      -v, --version          print updater version"
	echo "      -h, --help             give this help list"
	echo "      -c, --check            give this help list"
	echo

	version
}

function main() {
	local __getopt=`getopt \
		-o svfhcu \
		--long silent,version,force,help,verbose,check,update \
		-n "$(get_filename_without_path ${0})" \
		-- "$@"`

	build_environment

	eval set -- "${__getopt}"
	while true ; do
		case "${1}" in
			-s|--silent)
				DEBUG_LEVEL=${WARNING}
				shift;;
			-f|--force)
				WITHOUT_USER_CONFIRM=true
				shift;;
			-v|--version)
				version
				shift;;
			--verbose)
				DEBUG_LEVEL=${VERBOSE}
				shift;;
			-h|--help)
				usage
				shift;;
			-c|--check)
				WITHOUT_USER_CONFIRM=true
				CHECK_UPDATE_MODE=true
				shift;;
			-u|--update)
				PROCEED_UPDATE_MODE=true
				shift;;
			--) shift ;	break;;
		esac
	done

	if [ ${CHECK_UPDATE_MODE} == true ]; then
		echo "update mode"
		check_update
		exit 1
	elif [ ${PROCEED_UPDATE_MODE} == true ]; then
		check_update_info
		proceed_update
	else
		check_update
		proceed_update
		exit 1
	fi
}

main $@
