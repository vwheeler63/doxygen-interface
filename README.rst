*****************
doxygen-interface
*****************
**Python Interface to Doxygen**

This is a work in progress that aims to eventually become a useful Python package.

Until then, it's contents are a set of Python modules that make working with Doxygen
easier, starting with ``doxygen_config.py``.


doxygen_config
**************
**Python Interface to Doxygen Config Files (Doxyfiles)**


Usage
=====

.. code:: python

    import doxygen_config
    ...
    # 1. Load configuration from Doxyfile.
    cfg = doxygen_config.DoxygenConfig()
    cfg.load(doxyfile_src_file)

    # 2. Get a list of Doxygen option names.
    opt_list = cfg.options()
    ok_to_proceed = cfg.is_valid_option('PREDEFINED') \
        and cfg.is_valid_option('INPUT')

    # 3. Update it.
    if ok_to_proceed:
        temp = cfg.value('PREDEFINED')
        temp = temp.replace('<<CONFIG_PATH>>', config_file)
        cfg.set('PREDEFINED', temp)

        temp = cfg.value('INPUT')
        temp = temp.replace('<<SRC>>', f'"{pjt_src_dir}"')
        cfg.set('INPUT', temp)

        cfg.set('OUTPUT_DIRECTORY', 'doxygen')
        cfg.set('GENERATE_HTML', 'NO')
        cfg.set('GENERATE_XML', 'YES')
        cfg.set('XML_OUTPUT', "xml")

    # 4. Save it.
    # The original comments and order of config options are preserved.
    # The ``bare`` argument discards comments from the output.
    cfg.save(cfg_dict, doxyfile_dst_file, bare=True)


Design Differences from ``doxygen-python-interface``
====================================================

- The DoxygenConfig class represents the actual Doxygen configuration,
  in alignment with O-O theory --- it is not just a place to store a
  set of functions that never needed to be a class.

- If the user does a default ``save()`` (not requesting a "bare"
  version of the Doxygen configuration), the saved Doxyfile
  should be a binary match to the original Doxyfile loaded.

  Exceptions:

  1.  Any trailing whitespace in original Doxyfile after the ``=``
      on empty options is not preserved.

  2.  Multi-line lists that had unaligned backslashes after them like this:

  .. code:: python

        EXCLUDE_PATTERNS       = */libs/barcode/code* \
                                 */libs/freetype/ft*  \
                                 */libs/gif/gif*      \
                                 */libs/lodepng/lode* \
                                 */libs/qrcode/qr* \
                                 */libs/thorvg/*  \
                                 */libs/tiny_ttf/stb* \
                                 */libs/tjpgd/tjp* \
                                 */others/vg_lite_tvg/vg*

  will be saved like this:

  .. code:: python

        EXCLUDE_PATTERNS       = */libs/barcode/code*      \
                                 */libs/freetype/ft*       \
                                 */libs/gif/gif*           \
                                 */libs/lodepng/lode*      \
                                 */libs/qrcode/qr*         \
                                 */libs/thorvg/*           \
                                 */libs/tiny_ttf/stb*      \
                                 */libs/tjpgd/tjp*         \
                                 */others/vg_lite_tvg/vg*

  ``doxygen-python-interface`` did not save the comments so an "edit in
  place" of a Doxyfile could be catastrophic if the comments were needed
  in the source Doxyfile as they often are in production scenarios.

- The ``save()`` method has an optional ``bare`` argument (default False)
  that can be used to save a "bare" version of the Doxyfile options,
  discarding the comments from the currently-loaded Doxyfile.

- Input values are preserved exactly as they were found.  The
  ``doxygen-python-interface``'s ``configParser`` class removed
  quotation marks from incoming values and added quotation marks
  to values containing spaces before storing them again.  While
  this "sounds nice", it was incompatible with Doxygen for every
  type of item that could have a "list" as a value, such as the
  PREDEFINED and ABBREVIATE_BRIEF options.

  Examples:

  .. code:: python

    PREDEFINED             = USE_LIST USE_TABLE USE_CHART

    PREDEFINED             = DOXYGEN CONFIG_PATH="/path with spaces/to/my_conf.h"

    PREDEFINED             = DOXYGEN \
                             CONFIG_PATH="/path with spaces/to/my_conf.h"

  These are all valid values for the PREDEFINED option and MUST NOT
  have quotes around any of them!  Can you imagine the havoc that would
  result if a Python module meant to handle Doxygen Doxyfiles altered
  Doxygen configuration items like this?

  .. code:: python

    PREDEFINED             = "USE_LIST USE_TABLE USE_CHART"

  Thus, it is up to the user to know when values he is changing
  have space(s) AND ALSO need quotes and take appropriate measures
  by adding quotes when needed and not otherwise.

- The storage of the list of Doxygen options is encapsulated
  in the instance of the DoxygenConfig class instead of being
  returned as a dictionary from the ``load...()`` function.
  Its values are readable and writeable via methods.  The
  end user is not able to add options that were not part
  of the original input Doxyfile, nor remove options that were
  part of the original input Doxyfile.  This gives some level of
  control on retaining valid Doxygen options.

  It is an error to attempt to set a value with an option name
  that does not exist in the configuration.  A NameError exception
  is raised if it is attempted.  Attempting to read the value of
  an option name that does not exist returns the value ``None``.

  While Doxygen options change from time to time, it is up to the
  end user to use ``doxygen -u Doxyfile`` to keep his input
  Doxyfile(s) up to date.



Storage
=======

The actual configuration values are represented in an internal
dictionary not intended to be accessed directly by the typical end
user.  The keys are the Doxygen option names and the values are:

- str :  single values with possibly embedded spaces
- list:  multi-line values with possibly embedded spaces

Quotation marks are neither removed nor added, so it is up to the
user to set values compatible with Doxygen configuration syntax.
This also makes it okay for multi-line values to have more than one
value per line:  if it is okay by Doxygen, then it is okay by
the DoxygenConfig class.

If the user sets an option value passing a list, those values
will be represented as a multi-line value in the saved Doxyfile.



The Philosophy of Removing Quotation Marks Is Not Workable for Doxygen
======================================================================

When one asks, "Is it appropriate to remove the quotation marks?"
What if a value looked like this (2 quoted items in one line),
removing quotation marks would be an error:

.. code:: text

    "abc def" "ghi jkl"

The ABBREVIATE_BRIEF list could indeed appear like this.

If it were argued that all multi-value items should be formatted as
multi-line lists, then quotation marks theory works, as the
ABBREVIATE_BRIEF option does not require quotation marks around
every value.

However, since Doxygen does not require this, there is still a
strong argument for not tampering with quotation marks at all
when importing values.  The strongest reasons are:

-   Doxygen can and does accept values like this where the value of
    an option can be a list.  Doxygen sees this as 2 separate values:

    .. code:: text

        "abc def" "ghi jkl"

-   If the end user is going to set values with spaces in them,
    it could be made the user's responsibility to know when
    there are spaces and thus include quotes when needed.

In the end, the "do not tamper with quotation marks" argument wins
for sake of reliability.  So the policy is:  quotation marks are
neither removed nor added.  It is up to the user to know when they
are needed and add them himself.

