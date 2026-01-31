import json
import os
# Avoid importing tkinter on macOS builds where the bundled Tcl/Tk aborts
# Force terminal mode; users with working Tk can set TK_FORCE_GUI env var.
TK_AVAILABLE = False
tk = None
ttk = None
import curses
import time


SAVE_FILE = os.path.join(os.path.dirname(__file__), "cookie_save.json")


class Upgrade:
	def __init__(self, name, base_price, cps, click_power=0):
		self.name = name
		self.base_price = base_price
		self.cps = cps
		self.click_power = click_power
		self.amount = 0

	@property
	def price(self):
		# price scales by 15% per purchase
		return int(self.base_price * (1.15 ** self.amount))


class CookieClicker:
	def __init__(self, root):
		self.root = root
		root.title("Cookie Clicker - Mini")

		self.cookies = 0.0
		self.total_cookies = 0.0

		# base click gives 1 cookie
		self.base_click = 1

		# define upgrades
		self.upgrades = [
			Upgrade("Cursor", 15, cps=0.1),
			Upgrade("Grandma", 100, cps=1),
			Upgrade("Farm", 1100, cps=8),
		]

		# UI layout
		main = ttk.Frame(root, padding=12)
		main.pack(fill=tk.BOTH, expand=True)

		# cookie display + button
		top = ttk.Frame(main)
		top.pack(side=tk.TOP, fill=tk.X)

		self.cookies_var = tk.StringVar()
		self.cps_var = tk.StringVar()

		lbl_cookies = ttk.Label(top, textvariable=self.cookies_var, font=("Helvetica", 16))
		lbl_cookies.pack(side=tk.LEFT, padx=(0, 12))

		lbl_cps = ttk.Label(top, textvariable=self.cps_var, font=("Helvetica", 12))
		lbl_cps.pack(side=tk.LEFT)

		cookie_btn = ttk.Button(main, text="🍪 Click", command=self.click_cookie)
		cookie_btn.pack(fill=tk.BOTH, expand=True, pady=8, ipady=20)

		# upgrades frame
		store = ttk.LabelFrame(main, text="Store")
		store.pack(fill=tk.BOTH, expand=True)

		self.upgrade_frames = []
		for up in self.upgrades:
			f = ttk.Frame(store)
			f.pack(fill=tk.X, pady=4)
			name = ttk.Label(f, text=up.name)
			name.pack(side=tk.LEFT)
			amt = ttk.Label(f, text=f"Owned: {up.amount}")
			amt.pack(side=tk.LEFT, padx=8)
			price = ttk.Label(f, text=f"Price: {up.price}")
			price.pack(side=tk.LEFT, padx=8)
			btn = ttk.Button(f, text="Buy", command=lambda u=up: self.buy(u))
			btn.pack(side=tk.RIGHT)
			self.upgrade_frames.append((up, amt, price, btn))

		# bottom controls
		bottom = ttk.Frame(main)
		bottom.pack(fill=tk.X, pady=(8, 0))
		save_btn = ttk.Button(bottom, text="Save", command=self.save)
		save_btn.pack(side=tk.LEFT)
		load_btn = ttk.Button(bottom, text="Load", command=self.load)
		load_btn.pack(side=tk.LEFT, padx=8)

		self.load()

		# allow spacebar to click the cookie
		self.root.bind("<space>", lambda e: self.click_cookie())

		# start CPS loop (10 times per second)
		self._tick_ms = 100
		self._running = True
		self._update_ui()
		self.root.protocol("WM_DELETE_WINDOW", self.on_close)

	def click_cookie(self, event=None):
		click_value = self.base_click + sum(u.click_power * u.amount for u in self.upgrades)
		self.cookies += click_value
		self.total_cookies += click_value
		self._update_ui()

	def buy(self, up: Upgrade):
		p = up.price
		if self.cookies >= p:
			self.cookies -= p
			up.amount += 1
			self._update_ui()

	def cps(self):
		return sum(u.cps * u.amount for u in self.upgrades)

	def _update_ui(self):
		# apply CPS increment
		if self._running:
			self.cookies += self.cps() * (self._tick_ms / 1000.0)
			self.total_cookies += self.cps() * (self._tick_ms / 1000.0)

		# update labels
		self.cookies_var.set(f"Cookies: {int(self.cookies)}")
		self.cps_var.set(f"CPS: {self.cps():.2f}")

		for up, amt_label, price_label, btn in self.upgrade_frames:
			amt_label.config(text=f"Owned: {up.amount}")
			price_label.config(text=f"Price: {up.price}")
			# enable/disable buy button based on affordability
			if self.cookies >= up.price:
				btn.config(state=tk.NORMAL)
			else:
				btn.config(state=tk.DISABLED)

		# schedule next tick
		if self._running:
			self.root.after(self._tick_ms, self._update_ui)

	def save(self):
		data = {
			"cookies": self.cookies,
			"total_cookies": self.total_cookies,
			"upgrades": [{"name": u.name, "amount": u.amount} for u in self.upgrades],
		}
		try:
			with open(SAVE_FILE, "w") as f:
				json.dump(data, f)
		except Exception:
			pass

	def load(self):
		if not os.path.exists(SAVE_FILE):
			return
		try:
			with open(SAVE_FILE, "r") as f:
				data = json.load(f)
			self.cookies = data.get("cookies", 0.0)
			self.total_cookies = data.get("total_cookies", 0.0)
			up_map = {u["name"]: u for u in data.get("upgrades", [])}
			for u in self.upgrades:
				u.amount = up_map.get(u.name, {}).get("amount", 0)
		except Exception:
			pass

	def on_close(self):
		self._running = False
		self.save()
		self.root.destroy()


def main():
	if TK_AVAILABLE:
		root = tk.Tk()
		app = CookieClicker(root)
		root.mainloop()
	else:
		terminal_main()


def terminal_main():
	stdscr = curses.initscr()
	curses.curs_set(0)
	stdscr.nodelay(True)
	stdscr.timeout(100)

	cookies = 0.0
	total_cookies = 0.0
	base_click = 1
	upgrades = [
		Upgrade("Cursor", 15, cps=0.1),
		Upgrade("Grandma", 100, cps=1),
		Upgrade("Farm", 1100, cps=8),
	]

	last = time.time()
	running = True
	try:
		while running:
			now = time.time()
			dt = now - last
			last = now
			# CPS income
			cps = sum(u.cps * u.amount for u in upgrades)
			cookies += cps * dt

			# draw UI
			stdscr.erase()
			stdscr.addstr(0, 0, "Cookie Clicker - Terminal")
			stdscr.addstr(1, 0, f"Cookies: {int(cookies)}   CPS: {cps:.2f}")
			stdscr.addstr(3, 0, "SPACE: click    1-3: buy    s: save    l: load    q: quit")
			for i, u in enumerate(upgrades, start=1):
				stdscr.addstr(4 + i, 0, f"{i}. {u.name} | Owned: {u.amount} | Price: {u.price}")

			stdscr.refresh()

			c = stdscr.getch()
			if c != -1:
				if c in (ord('q'), ord('Q')):
					running = False
				elif c == ord(' '):
					click_value = base_click + sum(u.click_power * u.amount for u in upgrades)
					cookies += click_value
					total_cookies += click_value
				elif c in (ord('1'), ord('2'), ord('3')):
					idx = int(chr(c)) - 1
					if 0 <= idx < len(upgrades):
						up = upgrades[idx]
						if cookies >= up.price:
							cookies -= up.price
							up.amount += 1
				elif c in (ord('s'), ord('S')):
					data = {
						"cookies": cookies,
						"total_cookies": total_cookies,
						"upgrades": [{"name": u.name, "amount": u.amount} for u in upgrades],
					}
					try:
						with open(SAVE_FILE, "w") as f:
							json.dump(data, f)
					except Exception:
						pass
				elif c in (ord('l'), ord('L')):
					if os.path.exists(SAVE_FILE):
						try:
							with open(SAVE_FILE, "r") as f:
								data = json.load(f)
							cookies = data.get("cookies", 0.0)
							total_cookies = data.get("total_cookies", 0.0)
							up_map = {u["name"]: u for u in data.get("upgrades", [])}
							for u in upgrades:
								u.amount = up_map.get(u.name, {}).get("amount", 0)
						except Exception:
							pass

			time.sleep(0.05)
	finally:
		curses.endwin()


if __name__ == "__main__":
	main()

