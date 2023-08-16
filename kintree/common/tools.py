import builtins
import json
import os
from shutil import copyfile


# CUSTOM PRINT METHOD
class pcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Overload print function with custom pretty-print


def cprint(*args, **kwargs):
    # Check if silent is set
    try:
        silent = kwargs.pop('silent')
    except:
        silent = False
    if not silent:
        if type(args[0]) is dict:
            return builtins.print(json.dumps(*args, **kwargs, indent=4, sort_keys=True))
        else:
            try:
                args = list(args)
                if 'warning' in args[0].lower():
                    args[0] = f'{pcolors.WARNING}{args[0]}{pcolors.ENDC}'
                elif 'error' in args[0].lower():
                    args[0] = f'{pcolors.ERROR}{args[0]}{pcolors.ENDC}'
                elif 'fail' in args[0].lower():
                    args[0] = f'{pcolors.ERROR}{args[0]}{pcolors.ENDC}'
                elif 'success' in args[0].lower():
                    args[0] = f'{pcolors.OKGREEN}{args[0]}{pcolors.ENDC}'
                elif 'pass' in args[0].lower():
                    args[0] = f'{pcolors.OKGREEN}{args[0]}{pcolors.ENDC}'
                elif 'main' in args[0].lower():
                    args[0] = f'{pcolors.HEADER}{args[0]}{pcolors.ENDC}'
                elif 'skipping' in args[0].lower():
                    args[0] = f'{pcolors.BOLD}{args[0]}{pcolors.ENDC}'
                args = tuple(args)
            except:
                pass
            return builtins.print(*args, **kwargs, flush=True)
###


def create_library(library_path: str, symbol: str, template_lib: str):
    ''' Create library files if they don\'t exist '''
    if not os.path.exists(library_path):
        os.mkdir(library_path)
    new_kicad_sym_file = os.path.join(library_path, f'{symbol}.kicad_sym')
    if not os.path.exists(new_kicad_sym_file):
        copyfile(template_lib, new_kicad_sym_file)


def download(url, filetype='API data', fileoutput='', timeout=3, enable_headers=False, requests_lib=False, silent=False):
    ''' Standard method to download URL content, with option to save to local file (eg. images) '''

    import socket
    import urllib.request
    import requests

    # Set default timeout for download socket
    socket.setdefaulttimeout(timeout)
    if enable_headers:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
    try:
        if filetype == 'Image' or filetype == 'PDF':
            # Enable use of requests library for downloading files (some URLs do NOT work with urllib)
            if requests_lib:
                headers = {'User-agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                if filetype.lower() not in response.headers['Content-Type'].lower():
                    cprint(f'[INFO]\tWarning: {filetype} download returned the wrong file type\n{response.headers["Content-Type"].lower()}', silent=silent)
                    return None
                with open(fileoutput, 'wb') as file:
                    file.write(response.content)
            else:
                (file, headers) = urllib.request.urlretrieve(url, filename=fileoutput)
                if filetype.lower() not in headers['Content-Type'].lower():
                    cprint(f'[INFO]\tWarning: {filetype} download returned the wrong file type\n{headers["Content-Type"].lower()}', silent=silent)
                    return None
            return file
        else:
            url_data = urllib.request.urlopen(url)
            data = url_data.read()
            data_json = json.loads(data.decode('utf-8'))
            return data_json
    except (socket.timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        cprint(f'[INFO]\tWarning: {filetype} download socket timed out ({timeout}s)', silent=silent)
    except (urllib.error.HTTPError, requests.exceptions.ConnectionError):
        cprint(f'[INFO]\tWarning: {filetype} download failed (HTTP Error)', silent=silent)
    except (urllib.error.URLError, ValueError, AttributeError):
        cprint(f'[INFO]\tWarning: {filetype} download failed (URL Error)', silent=silent)
    except requests.exceptions.SSLError:
        cprint(f'[INFO]\tWarning: {filetype} download failed (SSL Error)', silent=silent)
    except FileNotFoundError:
        cprint(f'[INFO]\tWarning: {os.path.dirname(fileoutput)} folder does not exist', silent=silent)
    return None


def download_with_retry(url: str, full_path: str, silent=False, **kwargs) -> str:
    ''' Standard method to download image URL to local file '''

    if not url:
        cprint('[INFO]\tError: Missing image URL', silent=silent)
        return False

    # Try without headers
    file = download(url, fileoutput=full_path, silent=silent, **kwargs)

    if not file:
        # Try with headers
        file = download(url, fileoutput=full_path, enable_headers=True, silent=silent, **kwargs)

    if not file:
        # Try with requests library
        file = download(url, fileoutput=full_path, enable_headers=True, requests_lib=True, silent=silent, **kwargs)

    # Still nothing
    if not file:
        return False

    return True
