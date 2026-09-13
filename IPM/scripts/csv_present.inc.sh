# Source from run_*.sh. A 100 k archive is present if the CSV or a zip/gz sibling exists.
csv_present() {
  local p="$1"
  [[ -n "$p" ]] || return 1
  [[ -s "$p" || -s "${p}.zip" || -s "${p}.gz" ]]
}
