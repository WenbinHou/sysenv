
# sysenv
This utility makes you quite easy to manage your environment variables.

---

NOTE:
- This utility works with `bash` only!
- `env-mpi-select` is not finished yet!


## Installation

#### 1. `git clone` to your local disk.

Suppose it's cloned to `/sysenv`.
The cloned directory should be readable by everyone.

#### 2. Integrate `sysenv` into bash.

Just run
```
sudo python /sysenv/install.py
```

A line of `source /sysenv/env.bashrc` will be added to the proper file.
- For Ubuntu: Added to the top of `/etc/bash.bashrc`
- For CentOS: Added to the top of `/etc/bashrc`
- For other OS: The installer can't do it for you. Manually add the above line into your system-wide bash profile.


NOTE:
- `/sysenv/env.bashrc` is sourced no matter `bash` is interactive or not.
- `/sysenv/env.bashrc` is sourced even if `bash` is started by SSH.
- Idempotence: to source `/sysenv/env.bashrc` many times is OK.


## Usage

### 1. Use `~/env.conf` to define environment variables.

It's quite easy to define environment variables using `~/env.conf`

`env.conf` has a simple ini-style syntax:
- Multiple values of an environment variable is defined in multiple lines, they will be joined with colon `:` at last
- To reference environment variables (bash-style syntax: `$VAR` or `${VAR}`) when defining a environment variable is permitted
- "Internal" variables (starting with dot `.`) will not be exported, but they bring convenience
- Using special characters in environment variables is OK

*Please see `env.conf.example` for details.*

### 2. Bash Command: env-reload

````
env-reload
````
After changing your `~/env.conf`, use this command to reload the file.

Quite a few corner cases are considered and tests, feel safe and free to use this command!

**The effect is real-time, which means you DO NOT need to exit & restart your `bash`**

### 3. Bash Command: env-mpi-select

````
env-mpi-select              # This will show the information
env-mpi-select <target>     # This will switch to the target implementation
````

Use `env-mpi-select` to switch to a different MPI implementation.

**The effect is real-time, which means you DO NOT need to exit & restart your `bash`**


## Warning

NOT every corner cases are tested. So please take care when using any **strange** characters in path string.

For example:
- Back slashes `\`
- Colons `:`

Dollars `$$`, Whitespaces ` `, single quotes `'` and double quotes `"` should work.

However, it's still strongly suggested **NOT** including these characters in path string,
since not every program and library handles them very well.

## Similar Tools




## env.conf.example

````ini

###############################################################################
# Add your personal $PATH here
###############################################################################
[PATH]
/your/path1/bin
/your/path2/bin
/your/path3/bin


###############################################################################
# The following lines demonstrate how variant expansion works.
# Generally speaking, it's a cartesian product.
#
# With
#   FOO=ab:cd
#   BAR=123:456
# We have
#   $FOO$BAR=ab123:ab456:
###############################################################################
[FOO]
ab
cd

[BAR]
123
456

# DUMMY will be "ab123-xyz:ab456-xyz:cd123-xyz:cd456-xyz:ab233:cd233"
[DUMMY]
$FOO$BAR-xyz
${FOO}233


###############################################################################
# Use '$$' to escape a '$' character.
# Special characters are OK in the values, like:
# single quotes, double quotes, whitespaces, bask-slashes...
#
# In the following example, MY_VAR =
#   M\y$V:a "lu'e
###############################################################################
[MY_VAR]
M\y$$V:a "lu'e


###############################################################################
# Make it easy to set environment variables:
# - Multiple names in the same "[" "]" separated by whitespaces will be
#     assigned the same value
# - Dot-started names will NOT be exported, but they can be referenced in
#     other variables (for convenience)
#
# The following statements make it easy to add your self-compiled library's
#   paths into environment variables: LIBRARY_PATH, C_INCLUDE_PATH &
#   CPLUS_INCLUDE_PATH for compilers; PATH & LD_LIBRARY_PATH for executables,
#   MANPATH for man-documentation, PKG_CONFIG_PATH for pkg-config.
# If you place all your compiled library in the same root directory (NOT the
#   same "--prefix" option!), like ~/build, it's quite convenient to write
#   like the following. Now if you want to compile openssl, just run
#     ./configure --prefix=$HOME/build/libssl <other_options>
#     make && make install
#   and uncomment the libssl line below. Then run 'env-reload' - All done.
#
# As you have this tool, please DO NOT:
#   - Compile many libraries/executables with the same "--prefix" option
#   - Compile a library/executable with default option "--prefix" = /usr/local
#
###############################################################################

[.my_compiled_libs]
libpcre
libhmsbeagle
#libssl

[.my_install_root]
~/build/${.my_compiled_libs}

[LIBRARY_PATH LD_LIBRARY_PATH]
${.my_install_root}/lib
${.my_install_root}/lib64

[PKG_CONFIG_PATH]
${.my_install_root}/lib/pkgconfig

[C_INCLUDE_PATH CPLUS_INCLUDE_PATH]
${.my_install_root}/include

[MANPATH]
${.my_install_root}/share/man

[PATH]
${.my_install_root}/bin

````
