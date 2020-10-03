# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure_functions_worker import main
import multiprocessing

if __name__ == '__main__':
    multiprocessing.set_start_method('fork')
    main.main()
