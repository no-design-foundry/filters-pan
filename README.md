# Rastr

This is the Pan filter for [nodesignfoundry.com](https://nodesignfoundry.com)

It slices glyphs and creates visually rich variable font, based on the idea of Thom Janssen.


# CLI
- Ensure you have Python 3 installed by running `python -v` or `python3 -v` in your terminal.
- Verify that `git` is installed by executing `git -v` in your terminal. If the git version is displayed, you're all set. Otherwise, proceed with installing git.
- Install the plugin for Python using the following command: `python -m pip install git+https://github.com/no-design-foundry/filters-pan.git`
- You run the tool in terminal via `pan <hinted font> <step>`. This will rasterize the font and output `.ufo` file next to your input file.
- There is additional argument `--output-dir` that will save the `.ufo` file to given folder

