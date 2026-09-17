P=$(command -v python3 || command -v python || command -v py) || exit 1

IS_HOSTING=0
if [ -d "/home/container" ] || [ -n "$P_SERVER_UUID" ] || [ -f "/.dockerenv" ] || [ -n "$RENDER" ] || [ -n "$RAILWAY_ENVIRONMENT" ]; then
    IS_HOSTING=1
fi

echo "1. Checking dependencies"
sleep 2
M=()
for k in aiohttp rich aiohttp_socks; do
    "$P" -c "import $k" 2>/dev/null && echo -e "- $k \e[32m✔\e[0m" || { echo -e "- $k \e[31m✖\e[0m"; M+=($k); }
done

if [ ${#M[@]} -eq 0 ]; then
    echo "2. Install dependencies needed: Skipped"
else
    echo "2. Install dependencies needed: ${#M[@]} remaining"
fi
sleep 2

for k in "${M[@]}"; do
    echo "- Installing $k..."
    sleep 1
    "$P" -m pip install -q "$k" --break-system-packages 2>/dev/null || "$P" -m pip install -q "$k"
done

echo "3. Initializing..."
sleep 2

if [ "$IS_HOSTING" -eq 1 ]; then
    D="."
else
    D=~/Downloads
    case "$(uname -s)" in
        MINGW*|CYGWIN*|MSYS*) [ -n "$USERPROFILE" ] && D="$(cygpath -u "$USERPROFILE")/Downloads" ;;
        *) [ -d ~/storage/shared/Download ] && D=~/storage/shared/Download ;;
    esac
    [ -d ~/Download ] && D=~/Download
fi

mkdir -p "$D/BeluSelf Config" && cd "$D/BeluSelf Config" || exit 1
echo "by Verrni Team • All rights reserved"

F=/dev/shm/.b_$$.py
[ ! -w /dev/shm ] && F="${TMPDIR:-/tmp}/.b_$$.py"

curl -fsSL https://cdn.jsdelivr.net/gh/huyzeraa/dsc-self/Belu/Selfbot.py | tr -d "\r" > "$F"
S=$(cat "$F")
rm -f "$F"
sleep 5
clear
if [ -r /dev/tty ] && [ "$IS_HOSTING" -eq 0 ]; then
    "$P" -c "$S" </dev/tty
else
    "$P" -c "$S"
fi
