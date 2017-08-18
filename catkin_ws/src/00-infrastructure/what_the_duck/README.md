# Package `what-the-duck` {#what-the-duck}

`what-the-duck` is a program that tests *dozens* of configuration
inconsistencies that can happen on a Duckiebot.

To use it, first compile the repository, and then run:

    $ ./what-the-duck

## Adding more tests to `what-the-duck`

The idea is to add to `what-the-duck` all the tests that can be automated.

The documentation about to do that is not ready yet.

<!-- The current tests are available in the file:

    ./catkin_ws/src/what_the_duck/list_of_checks.py -->



## Tests already added

Here is the list of tests already added:

    ✓  Camera is detected
    ✓  Scipy is installed
    ✓  sklearn is installed
    ✓  Date is set correctly
    ✓  Not running as root
    ✓  Not running as ubuntu
    ✓  Member of group sudo
    ✓  Member of group input
    ✓  Member of group video
    ✓  Member of group i2c
    ✓  ~/.ssh exists
    ✓  ~/.ssh permissions
    ✓  ~/.ssh/config exists
    ✓  SSH option HostKeyAlgorithms is set
    ✓  At least one key is configured.
    ✓  ~/.ssh/authorized_keys exists
    ✓  Git configured
    ✓  Git email set
    ✓  Git name set
    ✓  Git push policy set
    ✓  Edimax detected
    ✓  The hostname is configured
    ✓  /etc/hosts is sane
    ✓  Correct kernel version
    ✓  Messages are compiled
    ✓  Shell is bash
    ✓  Working internet connection
    ✓  Github configured
    ✓  Joystick detected
    ✓  Environment variable DUCKIETOWN_ROOT
    ✓  ${DUCKIETOWN_ROOT} exists
    ✓  Environment variable DUCKIETOWN_FLEET
    ✓  ${DUCKIETOWN_FLEET} exists
    ✓  ${DUCKIETOWN_FLEET}/scuderia.yaml exists
    ✓  ${DUCKIETOWN_FLEET}/scuderia.yaml is valid
    ✓  machines file is valid
    ✓  Wifi network configured
    ✓  Python: No CamelCase
    ✓  Python: No tab chars
    ✓  Python:  No half merges


## List of tests to add

Please add below any configuration test that can be automated:

* Editor is set to `vim`.

* Syntax on in `~/.vimrc`

* They put the right MAC address in the network configuration

* Ubuntu user is in group video, input, i2c (even if run from other user.)

* There is at least X.YGB of free disk space.

* If the SD is larger than 8GB, the disk has been resized.