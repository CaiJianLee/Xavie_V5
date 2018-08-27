export PYTHON_HOME=/opt/seeing/app
export XAVIER_LOG_PATH=/opt/seeing/log
export XAVIER_CONFIG_PATH=/opt/seeing/config
export LD_LIBRARY_PATH=$PYTHON_HOME/lib:$PYTHON_HOME/lib/libc:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHON_HOME/packages:$PYTHON_HOME:$PYTHONPATH
export ARM_BOARD_IP="127.0.0.1"
export PATH=$PATH:$PYTHON_HOME/../tools/arm-xavier-toolset/bin/
