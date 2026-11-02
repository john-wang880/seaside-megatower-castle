# Current v030 replay

Use `qa/v030_current/export_four.py` to create fresh default/OFF/HIGH/LOW copies, then `qa/v030_current/run_qa.py`. Full explicit commands are in that bundle README. Current source is9f020b7e…feda35; the LOW-tree comparison separately uses byte-exact historical v018 c46b581a…44cfd from commit89cce41edf648eef6487d54ee1ce2a46bbb0ae17. Never replace the current source with that historical scene.

All processes are sequential and explicit. Use new external output directories and inherited PYTHONDONTWRITEBYTECODE=1. No downloads/installs/rendering or automatic UI execution. Linux native validation passed; Windows remains untested.
