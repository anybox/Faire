#!/bin/bash
USAGE=$(cat <<-END
\n ======================================\n
Allows to quickly launch a single test \n
======================================\n\n
  \e[1;3;30musage:\e[0m\n
  ./test.sh \e[1;32menvelope\e[0m\n
\t╰▶ will launch \e[1;32mclocky/test/test_envelope.py\033[0m\n
\n
  \e[1;3;30mtips:\e[0m\n
  ┌──────────────────────────────────────────────────┐\n
  │ find \e[32m-name \e[34m'*.py'\e[0m|entr \e[32m-c ./test.sh\e[0m generate_cra │\n
  └──────────────────────────────────────────────────┘\n
 ╰▶ will relauch the test every time a py file is saved (requires \e[1;30mentr\e[0m)\n
END
)

test_file="clocky/tests/test_$1.py"


if test -f $test_file; then
docker-compose \
   -f docker-compose.yml -f docker-compose.dev.yml run clocky bash -c \
			"rm cra/*; nosetests --nologcapture --tests $test_file -s -v"
else
  echo -e $USAGE
  echo -e "ERROR: \e[1;31m$test_file\033[0m not found"
fi
