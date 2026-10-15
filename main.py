"""Generates output.gif: login -> password -> fetch.sh -> profile output -> git commit."""
import profile_data as P
from terminal import Terminal, FG, GREEN, CYAN, YELLOW, PURPLE, DIM

KEY_W = 15


def render_section(t, title, rows):
    t.out([(title, CYAN)], 70)
    t.out([("-" * len(title), DIM)], 40)
    for row in rows:
        if isinstance(row, tuple):
            key, val = row
            segs = [((key + ":").ljust(KEY_W) if key else " " * KEY_W, YELLOW), (val, FG)]
        elif row.startswith("•"):
            segs = [("•", GREEN), (row[1:], FG)]
        else:
            segs = [(row, FG)]
        t.out(segs, 55)
    t.out("", 40)
    t.pause(900, cursor=False)  # let the reader catch up


def main():
    t = Terminal(title=f"{P.USER}@{P.HOST}: ~")

    # --- login screen ---
    t.out([("━" * 52, CYAN)], 90)
    t.out([("  A B H I N A V   J H A", GREEN), ("   //   secure access node", CYAN)], 90)
    t.out([("━" * 52, CYAN)], 90)
    t.out([("encrypted session · authorised builders only", DIM)], 150)
    t.out("", 60)
    t.write("identify yourself › ", PURPLE)
    t.pause(700)
    t.type(P.USER, per_char=110)
    t.enter(300)
    t.write("passphrase › ", PURPLE)
    t.pause(500)
    t.type("", per_char=0)
    for _ in range(9):               # typed password is masked (no echo like a real tty, shown as dots)
        t.write("•", DIM)
        t.snap(95)
    t.enter(500)
    t.out([("✔ access granted — welcome back, Abhinav", GREEN)], 400)
    t.out("", 60)

    # --- fetch.sh ---
    t.prompt(P.USER, P.HOST)
    t.pause(600)
    t.type(P.COMMAND, per_char=65)
    t.enter(400)
    for title, rows in P.SECTIONS:
        render_section(t, title, rows)

    # --- git commit ---
    t.prompt(P.USER, P.HOST)
    t.pause(500)
    t.type(f'git commit -am "{P.COMMIT_MSG}"', per_char=65)
    t.enter(500)
    t.out([("[main ", FG), ("a1b2c3d", YELLOW), (f"] {P.COMMIT_MSG}", FG)], 300)
    t.out([(" 1 file changed, 1 insertion(+)", DIM)], 300)
    t.prompt(P.USER, P.HOST)
    for _ in range(4):               # blinking cursor before the loop restarts
        t.snap(550, cursor=True)
        t.snap(450, cursor=False)

    frames, secs = t.save("output.gif")
    print(f"output.gif: {frames} frames, {secs:.1f}s")


if __name__ == "__main__":
    main()
