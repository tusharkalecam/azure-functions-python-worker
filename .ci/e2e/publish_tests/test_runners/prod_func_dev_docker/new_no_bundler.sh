#!/usr/bin/env bash

# Get the configuration variables
source "$(dirname "${BASH_SOURCE[0]}")/../helpers/get_config_variables.sh"

FUNCTION_APP="$(cat "${GLOBAL_CONFIG}" | jq -r '.publish_function_app.prod_func_dev_docker.new_function.no_bundler')"

"$(dirname "${BASH_SOURCE[0]}")/../../func_tests_core/new_functionapp/no_bundler_test.sh" ${WORKING_DIR}/pfddnnb ${FUNCTION_APP} func ${DEV_DOCKER_IMAGE}