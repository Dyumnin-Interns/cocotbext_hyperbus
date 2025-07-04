# Contributing

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Areas for contribution
The project follows a modular approach to make it easier to support new RTL Generators and Testcases.

### Adding support for a new RTL Coding style.

There are dozens of proprietary and opensource tools for generating RTL code from IP-XACT, SystemRDL, CSV or other inhouse formats.
These tools will define their fields in a fixed pattern, e.g. `<prefix>_<RegisterName>_<signalName>` or `<signalName>` or ...

To add support to a particular style of signal naming,

1. create a new file under `src/cocotbext/hyperbus/callbacks/bsv.py`
	2.  Preferably name the file as <toolname>.py
3. define your class and define the read and write functions in it.
4. submit a PR.

### Adding support for a new TestCases.
The current version of hyperbus supports reset check and simple rw_test with foreground and background read/write combinations.
There are a bunch of additional tests that are normally written for checking registers.
To contribute a new test:
1. Add your test to `src/cocotbext/hyperbus/testcases` folder
2. Submit a PR.



## Environment setup

Nothing easier!

Fork and clone the repository, then:

```bash
cd cocotbext/hyperbus
pdm install
```

> NOTE:
> If it fails for some reason,
> you'll need to install
> [PDM](https://github.com/pdm-project/pdm)
> manually.
>
> You can install it with:
>
> ```bash
> python3 -m pip install --user pipx
> pipx install pdm
> ```
>
> Now you can try running `pdm install`.

You now have the dependencies installed.



## Tasks

This project uses [duty](https://github.com/pawamoy/duty) to run tasks.
A Makefile is also provided. The Makefile will try to run certain tasks
on multiple Python versions. If for some reason you don't want to run the task
on multiple Python versions, you run the task directly with `pdm run duty TASK`.

The Makefile detects if a virtual environment is activated,
so `make` will work the same with the virtualenv activated or not.


## Development

As usual:

1. create a new branch: `git switch -c feature-or-bugfix-name`
1. edit the code and/or the documentation

**Before committing:**

1. run `pdm run duty format` to auto-format the code
1. run `pdm run duty check` to check everything (fix any warning)
1. run `make C tests` to run the tests (fix any issue)
1. if you updated the documentation or the project dependencies:
    1. run `pdm run duty docs`
    1. go to http://localhost:8000 and check that everything looks good
1. follow our [commit message convention](#commit-message-convention)

If you are unsure about how to fix or ignore a warning,
just let the continuous integration fail,
and we will help you during review.

Don't bother updating the changelog, we will take care of this.

## Commit message convention

Commit messages must follow our convention based on the
[Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message)
or the [Karma convention](https://karma-runner.github.io/4.0/dev/git-commit-msg.html):

```
<type>[(scope)]: Subject

[Body]
```

**Subject and body must be valid Markdown.**
Subject must have proper casing (uppercase for first letter
if it makes sense), but no dot at the end, and no punctuation
in general.

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `deps`: Dependencies update.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes that are not features or bug fixes.
- `style`: A change in code style/format.
- `tests`: About tests.

If you write a body, please add trailers at the end
(for example issues and PR references, or co-authors),
without relying on GitHub's flavored Markdown:

```
Body.

Issue #10: https://github.com/namespace/project/issues/10
Related to PR namespace/other-project#15: https://github.com/namespace/other-project/pull/15
```

These "trailers" must appear at the end of the body,
without any blank lines between them. The trailer title
can contain any character except colons `:`.
We expect a full URI for each trailer, not just GitHub autolinks
(for example, full GitHub URLs for commits and issues,
not the hash or the #issue-number).

We do not enforce a line length on commit messages summary and body,
but please avoid very long summaries, and very long lines in the body,
unless they are part of code blocks that must not be wrapped.

## Pull requests guidelines

Link to any related issue in the Pull Request message.

During the review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash main
```

And force-push:

```bash
git push -f
```

If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
