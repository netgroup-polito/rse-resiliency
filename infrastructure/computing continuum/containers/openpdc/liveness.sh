 #!/bin/sh

if test $(ss -ltn | grep -c 8500) -ge 1 -a $(ss -ltn | grep -c 6165) -ge 1; then
  echo "ok"
else
  exit 1
fi