import os    
test_library=os.environ.get("PROJECT")
fuzz_tool=0
bug_timeline_targets_run=False
timeout=10
hard_timeout=1800
max_length_fuzz_bytes=15000
parallel_execution=False
crash_limit=1000
log_report=True
# cc = "gcc -g -O0 -w -fprofile-generate"
primary_cc = "afl-clang-fast -g -O0 -w -fprofile-instr-generate -fcoverage-mapping"
cc = primary_cc
# cxx = "clang++"

# TODO this needs to be constructed dynamically
includes_locations = (
    os.path.abspath(f"/src/{test_library}/include"),
    os.path.abspath(f"/src/{test_library}"),
    os.path.abspath(f"/src/{test_library}/apps"),
    os.path.abspath(f"/src/{test_library}/apps/include"),
    os.path.abspath(f"/src/{test_library}/testcasesupport"),
)

lib_clone_location = f"/src/{test_library}"
lib_info_location = f"/work"
temp_work = f"/work/tmp"
temp_loc = os.path.abspath(os.path.join(lib_clone_location))
test_location = f"/work/test_files"
rats_log = f"/work/rats_logs"
pickle_name = test_library.replace("/", "_")
pickler = f"/work/{pickle_name}"
unrefined_targets = f"/work/targets-unrefined.txt"
targets = f"/work/targets.txt"
build_log = f"/work/build_logs_fixed"
xml_location = f"/work/srcml.xml"
out_location = f"/work/out"
std_out_location = f"/work/out.txt"
log_location = f"/work/log.txt"
bear_config_path = f"/decompileeval/FuzzSlice/bear_config.json"
fuzzer_location = f"/out"
info_path = f"/work/info.json"
delim = ".@."