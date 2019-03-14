Contribution guide
===================================

If you want to contribute to OMniLeads development you can open an issue at https://gitlab.com/omnileads/ominicontacto/issues (1) and ,optionally, a merge-request with the proposal code to solve it, following the next steps:

  * Create development environment from an installed system (see installation instructions)
  * Create an issue in (1) and take its number (_issue-number_ for the rest of the text)
  * Fork and clone the repository locally
  * Create a branch from the last 'develop' version in the repository
      * Write clear, concise and well documented code
      * Name the  branch following the schema _oml-ext-issue-number-clear-description_
      * Follow PEP8 coding style as specified in file .flake8 in the root repository folder
      * Make sure the unit testing system remains without errors in its execution
      * If a new feature is added to the system the develop must write unit tests to document it correctly
      * Updates the issue branch against the most recent 'develop' previous to make the merge-request using 'rebase', this is:
          * $ git rebase develop
      * Upload the branch to the repository:
          * $ git push origin _oml-ext-issue-number-clear-description_
      * Create the merge-request from repository interface
