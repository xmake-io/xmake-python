ifeq ($(OS),Windows_NT)
  DLL_EXT := pyd
else
  DLL_EXT := so
endif

OSTYPE := $(shell sh -c 'echo $$OSTYPE')
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_M),x86_64)
  ifeq ($(OS),Windows_NT)
    CPU := _amd64
  else
    CPU := x86_64
  endif
endif
ifneq ($(filter %86,$(UNAME_M)),)
  ifeq ($(OS),Windows_NT)
    CPU := 32
  else
    CPU := x86
  endif
endif
ifneq ($(filter arm%,$(UNAME_M)),)
  ifneq ($(filter arm64%,$(UNAME_M)),)
    ifeq ($(OS),Windows_NT)
      CPU := _arm64
    else
      CPU := aarch64
    endif
  else
    ifeq ($(OS),Windows_NT)
      CPU := _arm
    else
      CPU := arm
    endif
  endif
endif

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  ARCH := darwin
else
  ifeq ($(OS),Windows_NT)
    ARCH := win$(CPU)
  else
    ARCH := $(CPU)-$(OSTYPE)
  endif
endif

# we skip pypy
PY_VERSION := $(shell python -c 'import sys; print(f"{sys.version_info[0]}{sys.version_info[1]}")')
ifeq ($(OS),Windows_NT)
  PY := cp$(PY_VERSION)
else
  PY := cpython-$(PY_VERSION)
endif

# pypy310-pp73-x86_64-linux-gnu.so
# pypy310-pp73-win_amd64.pyd
# cpython-313-darwin.so
# cp313-win_amd64.pyd
PYD_EXT=$(PY)-$(ARCH).$(DLL_EXT)
