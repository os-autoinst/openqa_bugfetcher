SH_FILES ?= $(shell file --mime-type $$(git ls-files) test/*.t 2>/dev/null | sed -n 's/^\(.*\):.*text\/x-shellscript.*$$/\1/p')
SH_SHELLCHECK_FILES ?= $(shell file --mime-type * 2>/dev/null | sed -n 's/^\(.*\):.*text\/x-shellscript.*$$/\1/p')
PY_FILES ?= $(shell set -o pipefail; file --mime-type $$(git ls-files) | grep -E 'text/x-script\.python|text/x-python' | cut -d: -f1)
RUNNER ?= uv run

ifndef CI
include .setup.mk
endif

ifndef test
test := test/
ifdef GIT_STATUS_IS_CLEAN
test += xt/
endif
endif

PROVE ?= tools/prove_wrapper
BPAN := .bpan

#------------------------------------------------------------------------------
# User targets
#------------------------------------------------------------------------------
.PHONY: help
help: ## Show this help
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

default: help

# Override to use uv, e.g. PYTHON_RUN="uv run"
PYTHON_RUN ?=

.PHONY: test
ifeq ($(CHECKSTYLE),0)
checkstyle_tests =
else
checkstyle_tests = checkstyle
endif
test: $(checkstyle_tests) test-unit ## Run style checks and unit tests

test-unit: test-bash test-python ## Run all unit tests (bash and python)

test-bash: $(BPAN) ## Run bash tests
	@if [ -d test ] || [ -d xt ]; then "${PROVE}" -r $(if $v,-v )$(test); else echo "No bash tests found."; fi

.PHONY: test-python
test-python: ## Run python tests
	@if [ -d tests ]; then $(PYTHON_RUN) pytest tests; else echo "No python tests found."; fi

checkstyle: test-shellcheck test-yaml checkstyle-python check-code-health test-gitlint ## Run all style checks

shfmt: ## Format shell scripts
	@if [ -n "${SH_FILES}" ]; then shfmt -w ${SH_FILES}; fi

.PHONY: check-file-command
check-file-command:
	@command -v file >/dev/null 2>&1 || (echo "Error: 'file' command is not installed. It is required to detect script languages." && false)

test-shellcheck: check-file-command ## Run shell script checks
	@which shfmt >/dev/null 2>&1 || echo "Command 'shfmt' not found, can not execute shell script formating checks"
	@if [ -n "${SH_FILES}" ]; then shfmt -d ${SH_FILES}; fi
	@which shellcheck >/dev/null 2>&1 || echo "Command 'shellcheck' not found, can not execute shell script checks"
	@if [ -n "${SH_SHELLCHECK_FILES}" ]; then shellcheck -x ${SH_SHELLCHECK_FILES}; fi

test-yaml: ## Run YAML syntax checks
	@which yamllint >/dev/null 2>&1 || echo "Command 'yamllint' not found, can not execute YAML syntax checks"
	yamllint --strict $$(git ls-files "*.yml" "*.yaml" ":!external/")

.PHONY: checkstyle-python
checkstyle-python: check-ruff check-conventions check-ty ## Run python style checks

check-ruff: check-file-command ## Run python style checks with ruff
	@which ruff >/dev/null 2>&1 || echo "Command 'ruff' not found, can not execute python style checks"
	@if [ -n "$(PY_FILES)" ]; then $(PYTHON_RUN) ruff format --check $(PY_FILES) && $(PYTHON_RUN) ruff check $(PY_FILES); fi

check-conventions: ## Check project conventions
	@if [ -d tests ] && git grep -nE '^\s*@(unittest\.mock\.|mock\.)?patch' tests/; then \
		echo "Error: @patch decorator detected. Avoid to prevent argument ordering bugs."; \
		echo "   Fix: Use the 'mocker' fixture (pytest-mock) or a 'with patch():' context manager."; \
		exit 1; \
	fi

.PHONY: check-ty
check-ty: ## Run ty type checker
	$(PYTHON_RUN) ty check

check-code-health: ## Run code health checks (vulture)
	@echo "Checking code health…"
	@$(RUNNER) vulture $$(git ls-files "**.py") --min-confidence 80

.PHONY: test-with-coverage
test-with-coverage:
	@echo "No tests to run with coverage."

.PHONY: install-python-deps
install-python-deps:
	$(RUNNER) pip install -e .[dev]

.PHONY: test-gitlint
test-gitlint: ## Run commit message checks using gitlint
	@command -v gitlint >/dev/null 2>&1 || (echo "Command 'gitlint' not found, can not execute commit message checks. Install with 'python3-gitlint' (openSUSE) or 'pip install gitlint-core'" && false)
	@BASES=$$(for i in upstream/master upstream/main origin/master origin/main master main; do git rev-parse --verify $$i 2>/dev/null; done ||:); \
	BASE=$$(git merge-base --independent $$BASES | head -n 1); \
	gitlint --commits "$$BASE..HEAD"

.PHONY: tidy
tidy: check-file-command ## Format code and fix linting issues
	$(PYTHON_RUN) ruff format $(PY_FILES)
	$(PYTHON_RUN) ruff check --fix $(PY_FILES)

clean: ## Clean up generated files
	$(RM) job_post_response
	$(RM) -r $(BPAN)
	$(RM) -r .pytest_cache/
	find . -name __pycache__ | xargs -r $(RM) -r

install-systemd-local: ## Install contained systemd units for local use (not meant for packaging)
	install -d -m 755 "$(DESTDIR)"/etc/systemd/system
	for i in systemd/*.{service,timer}; do \
		install -m 644 $$i "$(DESTDIR)"/etc/systemd/system ;\
	done

#------------------------------------------------------------------------------
# Internal targets
#------------------------------------------------------------------------------
$(BPAN):
	@if [ -d test ] || [ -d xt ]; then git clone https://github.com/bpan-org/bpan.git --depth 1 $@; fi
