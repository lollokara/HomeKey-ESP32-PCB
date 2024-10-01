env = DefaultEnvironment()
from os.path import join
from SCons.Script import COMMAND_LINE_TARGETS
board = env.BoardConfig()
mcu = board.get("build.mcu", "esp32")

target_firm = env.DataToBin(
    join("$BUILD_DIR", "${ESP32_FS_IMAGE_NAME}"), "$PROJECT_DATA_DIR"
)
env.NoCache(target_firm)
AlwaysBuild(target_firm)

fs = env.Alias("buildfs", target_firm)

def before_upload(source, target, env):
    env.Append(UPLOADERFLAGS=['$FS_START', join('$BUILD_DIR','${ESP32_FS_IMAGE_NAME}.bin')])


def after_build(source, target, env):
  build_dir = env.subst('$BUILD_DIR')
  firmware_path = join(build_dir, '${PROGNAME}.bin')
  fs_path = join(build_dir,'${ESP32_FS_IMAGE_NAME}.bin')
  merged_path = join(build_dir, "firmware_merged.bin")
  env.Execute(f'"$PYTHONEXE" "$OBJCOPY" --chip {mcu} merge_bin --fill-flash-size 4MB -o {merged_path} $FLASH_EXTRA_IMAGES $ESP32_APP_OFFSET {firmware_path} $FS_START {fs_path}')

if "buildfs" not in COMMAND_LINE_TARGETS:
  Default([fs])

env.Depends("upload", fs)
env.AddPreAction("upload", before_upload)
env.AddPostAction(join('$BUILD_DIR', '${PROGNAME}.bin'), after_build)