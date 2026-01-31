import json
import os
# Avoid importing tkinter on macOS builds where the bundled Tcl/Tk aborts
# Force terminal mode; users with working Tk can set TK_FORCE_GUI env var.
TK_AVAILABLE = False
tk = None
ttk = None
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


class UpgradeItem:
	"""One-time or repeatable upgrade that modifies game behaviour."""
	def __init__(self, name, price, kind, value, target=None):
		self.name = name
		self.price = price
		self.kind = kind  # 'click_add', 'global_cps_mult', 'building_cps_mult'
		self.value = value
		self.target = target
		self.amount = 0


class CookieClicker:
	def __init__(self, root):
		self.root = root
		root.title("Cookie Clicker - Mini")

		self.cookies = 0.0
		self.total_cookies = 0.0

		# base click gives 1 cookie
		self.base_click = 1

		# define buildings (automated CPS generators)
		self.upgrades = [
			Upgrade("Cursor", 15, cps=0.1),
			Upgrade("Grandma", 100, cps=1),
			Upgrade("Farm", 1100, cps=8),
			Upgrade("Mine", 12000, cps=47),
			Upgrade("Factory", 130000, cps=260),
		]

		# upgrade items (apply effects)
		self.upgrade_items = [
			UpgradeItem("Reinforced Clicks", 100, kind="click_add", value=1),
			UpgradeItem("Efficient Grandmas", 500, kind="building_cps_mult", value=2.0, target="Grandma"),
			UpgradeItem("Turbo CPS", 2000, kind="global_cps_mult", value=1.5),
		]

		# multipliers applied by upgrades
		self.cps_multiplier = 1.0
		self.building_multipliers = {}

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

		# upgrades (one-time/purchasable modifiers)
		upgrades_frame = ttk.LabelFrame(main, text="Upgrades")
		upgrades_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
		self.upgrade_item_frames = []
		for ui in self.upgrade_items:
			f2 = ttk.Frame(upgrades_frame)
			f2.pack(fill=tk.X, pady=4)
			name2 = ttk.Label(f2, text=ui.name)
			name2.pack(side=tk.LEFT)
			amt2 = ttk.Label(f2, text=f"Owned: {ui.amount}")
			amt2.pack(side=tk.LEFT, padx=8)
			price2 = ttk.Label(f2, text=f"Price: {ui.price}")
			price2.pack(side=tk.LEFT, padx=8)
			btn2 = ttk.Button(f2, text="Buy", command=lambda u=ui: self.buy_upgrade(u))
			btn2.pack(side=tk.RIGHT)
			self.upgrade_item_frames.append((ui, amt2, price2, btn2))

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

	def buy_upgrade(self, ui: UpgradeItem):
		if self.cookies >= ui.price:
			self.cookies -= ui.price
			ui.amount += 1
			# apply effect
			if ui.kind == "click_add":
				self.base_click += ui.value
			elif ui.kind == "global_cps_mult":
				self.cps_multiplier *= ui.value
			elif ui.kind == "building_cps_mult":
				self.building_multipliers[ui.target] = self.building_multipliers.get(ui.target, 1.0) * ui.value
			self._update_ui()

	def cps(self):
		total = 0.0
		for u in self.upgrades:
			bm = self.building_multipliers.get(u.name, 1.0)
			total += u.cps * u.amount * bm
		return total * self.cps_multiplier

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
			if self.cookies >= up.price:
				btn.config(state=tk.NORMAL)
			else:
				btn.config(state=tk.DISABLED)

		for ui, amt_label, price_label, btn in self.upgrade_item_frames:
			amt_label.config(text=f"Owned: {ui.amount}")
			price_label.config(text=f"Price: {ui.price}")
			if self.cookies >= ui.price:
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
			"upgrade_items": [{"name": ui.name, "amount": ui.amount} for ui in self.upgrade_items],
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
			# load upgrade items and reapply their effects
			uim_map = {u["name"]: u for u in data.get("upgrade_items", [])}
			# reset effects
			self.cps_multiplier = 1.0
			self.building_multipliers = {}
			for ui in self.upgrade_items:
				ui.amount = uim_map.get(ui.name, {}).get("amount", 0)
				for _ in range(ui.amount):
					if ui.kind == "click_add":
						self.base_click += ui.value
					elif ui.kind == "global_cps_mult":
						self.cps_multiplier *= ui.value
					elif ui.kind == "building_cps_mult":
						self.building_multipliers[ui.target] = self.building_multipliers.get(ui.target, 1.0) * ui.value
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
	print("Running Cookie Clicker in terminal mode (text interface). Type 'help' for commands.")

	cookies = 0.0
	total_cookies = 0.0
	base_click = 1
	upgrades = [
		Upgrade("Cursor", 15, cps=0.1),
		Upgrade("Grandma", 100, cps=1),
		Upgrade("Farm", 1100, cps=8),
		Upgrade("Mine", 12000, cps=47),
		Upgrade("Factory", 130000, cps=260),
	]

	upgrade_items = [
		UpgradeItem("Reinforced Clicks", 100, kind="click_add", value=1),
		UpgradeItem("Efficient Grandmas", 500, kind="building_cps_mult", value=2.0, target="Grandma"),
		UpgradeItem("Turbo CPS", 2000, kind="global_cps_mult", value=1.5),
	]

	cps_multiplier = 1.0
	building_multipliers = {}

	last = time.time()

	def show_status():
		cps = sum(u.cps * u.amount * building_multipliers.get(u.name, 1.0) for u in upgrades) * cps_multiplier
		print(f"\nCookies: {int(cookies)}   CPS: {cps:.2f}   Total: {int(total_cookies)}")
		print("Buildings:")
		for i, u in enumerate(upgrades, start=1):
			print(f" {i}. {u.name} | Owned: {u.amount} | Price: {u.price} | CPS each: {u.cps}")
		print("Upgrades:")
		for i, ui in enumerate(upgrade_items, start=1):
			print(f" {i}. {ui.name} | Owned: {ui.amount} | Price: {ui.price} | Effect: {ui.kind} {ui.value} {ui.target or ''}")
		print("Commands: click, buy <n>, buyup <n>, save, load, status, help, quit")

	# load autosave if present
	if os.path.exists(SAVE_FILE):
		try:
			with open(SAVE_FILE, "r") as f:
				data = json.load(f)
			cookies = data.get("cookies", 0.0)
			total_cookies = data.get("total_cookies", 0.0)
			up_map = {u["name"]: u for u in data.get("upgrades", [])}
			for u in upgrades:
				u.amount = up_map.get(u.name, {}).get("amount", 0)
			uim_map = {u["name"]: u for u in data.get("upgrade_items", [])}
			# reset effects and reapply
			cps_multiplier = 1.0
			building_multipliers = {}
			base_click = 1
			for ui in upgrade_items:
				ui.amount = uim_map.get(ui.name, {}).get("amount", 0)
				for _ in range(ui.amount):
					if ui.kind == "click_add":
						base_click += ui.value
					elif ui.kind == "global_cps_mult":
						cps_multiplier *= ui.value
					elif ui.kind == "building_cps_mult":
						building_multipliers[ui.target] = building_multipliers.get(ui.target, 1.0) * ui.value
		except Exception:
			pass

	show_status()

	while True:
		# apply CPS since last command
		now = time.time()
		dt = now - last
		last = now
		cps = sum(u.cps * u.amount * building_multipliers.get(u.name, 1.0) for u in upgrades) * cps_multiplier
		cookies += cps * dt
		total_cookies += cps * dt

		cmd = input(" > ").strip().lower()
		if not cmd:
			continue
		parts = cmd.split()
		if parts[0] in ("q", "quit", "exit"):
			print("Saving and exiting...")
			data = {
				"cookies": cookies,
				"total_cookies": total_cookies,
				"upgrades": [{"name": u.name, "amount": u.amount} for u in upgrades],
				"upgrade_items": [{"name": ui.name, "amount": ui.amount} for ui in upgrade_items],
			}
			try:
				with open(SAVE_FILE, "w") as f:
					json.dump(data, f)
			except Exception:
				pass
			break
		elif parts[0] in ("help", "h"):
			show_status()
		elif parts[0] in ("status", "s"):
			show_status()
		elif parts[0] == "click":
			click_value = base_click + sum(u.click_power * u.amount for u in upgrades)
			cookies += click_value
			total_cookies += click_value
			print(f"You clicked for {click_value} cookies.")
		elif parts[0] == "buy" and len(parts) > 1:
			try:
				idx = int(parts[1]) - 1
				if 0 <= idx < len(upgrades):
					up = upgrades[idx]
					if cookies >= up.price:
						cookies -= up.price
						up.amount += 1
						print(f"Bought 1 {up.name}.")
					else:
						print("Not enough cookies.")
				else:
					print("Invalid building index.")
			except ValueError:
				print("Invalid index.")
		elif parts[0] == "buyup" and len(parts) > 1:
			try:
				idx = int(parts[1]) - 1
				if 0 <= idx < len(upgrade_items):
					ui = upgrade_items[idx]
					if cookies >= ui.price:
						cookies -= ui.price
						ui.amount += 1
						if ui.kind == "click_add":
							base_click += ui.value
						elif ui.kind == "global_cps_mult":
							cps_multiplier *= ui.value
						elif ui.kind == "building_cps_mult":
							building_multipliers[ui.target] = building_multipliers.get(ui.target, 1.0) * ui.value
						print(f"Bought upgrade {ui.name}.")
					else:
						print("Not enough cookies.")
				else:
					print("Invalid upgrade index.")
			except ValueError:
				print("Invalid index.")
		elif parts[0] == "save":
			data = {
				"cookies": cookies,
				"total_cookies": total_cookies,
				"upgrades": [{"name": u.name, "amount": u.amount} for u in upgrades],
				"upgrade_items": [{"name": ui.name, "amount": ui.amount} for ui in upgrade_items],
			}
			try:
				with open(SAVE_FILE, "w") as f:
					json.dump(data, f)
				print("Saved.")
			except Exception:
				print("Save failed.")
		elif parts[0] == "load":
			if os.path.exists(SAVE_FILE):
				try:
					with open(SAVE_FILE, "r") as f:
						data = json.load(f)
					cookies = data.get("cookies", 0.0)
					total_cookies = data.get("total_cookies", 0.0)
					up_map = {u["name"]: u for u in data.get("upgrades", [])}
					for u in upgrades:
						u.amount = up_map.get(u.name, {}).get("amount", 0)
					uim_map = {u["name"]: u for u in data.get("upgrade_items", [])}
					# reset effects and reapply
					cps_multiplier = 1.0
					building_multipliers = {}
					base_click = 1
					for ui in upgrade_items:
						ui.amount = uim_map.get(ui.name, {}).get("amount", 0)
						for _ in range(ui.amount):
							if ui.kind == "click_add":
								base_click += ui.value
							elif ui.kind == "global_cps_mult":
								cps_multiplier *= ui.value
							elif ui.kind == "building_cps_mult":
								building_multipliers[ui.target] = building_multipliers.get(ui.target, 1.0) * ui.value
					print("Loaded.")
				except Exception:
					print("Load failed.")
			else:
				print("No save file.")
		else:
			print("Unknown command. Type 'help' for commands.")


if __name__ == "__main__":
	main()
