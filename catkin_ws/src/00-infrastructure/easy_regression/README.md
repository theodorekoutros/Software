# Package `easy_regression` {#easy_regression}

<move-here src="#easy_regression-autogenerated"/>

## Design goals

TODO: to write



## Formalization

Note: These are incomplete design notes.

A regression test is given by:

1. A log set. These are either physical logs or just
2. One or more log processors. These take a bag and write a bag. Multiple bags are merged.

3. One or more visualizers.
4. One of more statistics.
5. Acceptance conditions.

The regression test engine does the following.

It reads the log test. It makes the logs available. (This might imply downloading
the logs.)


A physical log is a physical .bag file. These are generated


    regression1.regression_test.yaml

    description:
    Simple regression test.
    a
    logs:
    - "vehicle:ferrari,length:<10"
    processors:
    - transformer: Identity
    stats:
    visualizers:



    identity.job_processors.yaml
    description:
    constructor: IdentityProcessor
    parameters:


    count:


    S is a dict of YAML

    processor: Bag -> Bag
    analyzer: Bag -> S
    reduce: S x S -> S
    display_test: S -> Display


## Language


Simple checks:

    v:analyzer/log/statistics == value
    v:analyzer/log/statistics &gt;= value
    v:analyzer/log/statistics &lt;= value
    v:analyzer/log/statistics &lt; value
    v:analyzer/log/statistics &gt; value

Check that it is in 10% of the value:

    v:analyzer/log/statistics ==[10%] value

Use `@date` to reference the test result at that date:

    v:analyzer/log/statistics ==[10%] v:analyzer/log/statistic@date

Use `~branch@date` to reference the value of a branch at a certain date:

    v:analyzer/log/statistics ==[10%] v:analyzer/log/statistic~branch@date

Use `?commit` to reference the value of a branch at a specific commit:

    v:analyzer/log/statistics ==[10%] v:analyzer/log/statistic?e9aa5f4