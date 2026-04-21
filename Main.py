import time
import keyboard
from pathlib import Path
from pynput.mouse import Controller, Button

# =========================
# 설정
# =========================
CTRL_HOLD_TIME = 0.02
FIRST_HOLD_TIME = 0.03
END_DELAY = 0.5
POLL_INTERVAL = 0.001
TIMING_FILE = "timings.txt"

# 기본 타이밍 리스트
DEFAULT_PEAK_TIMES = [
    0.5,
    1.0,
    2.0,
    3.0,
    4.9,
    5.7,
    6.5,
    7.1,
    8.0,
    8.5,
    9.8,
    11.2,
    12.1
]

mouse = Controller()


def load_peak_times(file_path: str, default_times: list[float]) -> list[float]:
    path = Path(file_path)

    if not path.exists():
        print(f"timings.txt 없음 -> 기본값 사용: {file_path}")
        return default_times.copy()

    result = []

    try:
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                try:
                    value = float(line)
                    result.append(value)
                except ValueError:
                    print(f'파싱 실패: "{line}" -> 기본값 사용')
                    return default_times.copy()

        if not result:
            print("timings.txt 비어 있음 -> 기본값 사용")
            return default_times.copy()

        result.sort()
        print(f"timings.txt 로드 성공: {file_path}")
        return result

    except Exception as e:
        print(f"timings.txt 읽기 실패: {e} -> 기본값 사용")
        return default_times.copy()


def wait_until(target_time, start_time):
    while True:
        if keyboard.is_pressed("esc"):
            raise KeyboardInterrupt

        if time.perf_counter() - start_time >= target_time:
            break

        time.sleep(POLL_INTERVAL)


def run_macro(peak_times):
    if not peak_times:
        print("타이밍 리스트가 비어 있습니다.")
        return

    print("▶ 실행 시작")
    print("목표 타이밍:", [round(t, 4) for t in peak_times])

    start = time.perf_counter()

    try:
        # 첫 타이밍까지 대기
        wait_until(peak_times[0], start)

        now = time.perf_counter() - start
        diff = now - peak_times[0]
        print(f"[{now:.4f}s] ▶ FIRST: Ctrl + Mouse Down | target={peak_times[0]:.4f}s | diff={diff:+.4f}s")

        # 첫 입력: Ctrl + 좌클릭
        keyboard.press("ctrl")
        mouse.press(Button.left)

        time.sleep(FIRST_HOLD_TIME)
        keyboard.release("ctrl")

        # 이후: 좌클릭 유지, Ctrl만 반복
        for i, t in enumerate(peak_times[1:], start=2):
            wait_until(t, start)

            now = time.perf_counter() - start
            diff = now - t
            print(f"[{now:.4f}s] ▶ {i}: Ctrl Press | target={t:.4f}s | diff={diff:+.4f}s")

            keyboard.press("ctrl")
            time.sleep(CTRL_HOLD_TIME)
            keyboard.release("ctrl")

        # 마지막 후 딜레이
        now = time.perf_counter() - start
        print(f"[{now:.4f}s] ▶ END DELAY START ({END_DELAY:.2f}s)")
        time.sleep(END_DELAY)

    except KeyboardInterrupt:
        now = time.perf_counter() - start
        print(f"[{now:.4f}s] ⛔ ESC로 중단")

    finally:
        try:
            keyboard.release("ctrl")
        except:
            pass

        try:
            mouse.release(Button.left)
        except:
            pass

        now = time.perf_counter() - start
        print(f"[{now:.4f}s] ■ 실행 종료")


def main():
    peak_times = load_peak_times(TIMING_FILE, DEFAULT_PEAK_TIMES)

    print("앤이공 사용 타이밍:")
    print([round(t, 4) for t in peak_times])

    print("\n👉 F6: 실행")
    print("👉 ESC: 실행 중 중단")
    print("👉 Ctrl + C: 프로그램 완전 종료")

    while True:
        keyboard.wait("f6")
        run_macro(peak_times)


if __name__ == "__main__":
    main()