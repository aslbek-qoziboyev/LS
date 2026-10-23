#!/usr/bin/python3
import subprocess, shutil, xml.etree.ElementTree as ET
from pathlib import Path
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk, Gdk

CONFIG=Path.home()/".config/touchegg/touchegg.conf"
GESTURES=[
("Ikki barmoq bilan surish","Oynalar orasida o'tish","SWIPE","2","LEFT","ALT+TAB"),
("Uch barmoq pastga","Ish stolini ko'rsatish, majburan yopish emas","SWIPE","3","DOWN","SUPER+D"),
("To'rt barmoq bilan surish","Ish stollari orasida o'tish","SWIPE","4","RIGHT","CTRL+ALT+RIGHT"),
("Pinch in","Ctrl + + yuborish","PINCH","2","IN","CTRL+PLUS"),
("Pinch out","Ctrl + - yuborish","PINCH","2","OUT","CTRL+MINUS"),
("Ikki barmoqni aylantirish","Ekran yo'nalishini almashtirish","ROTATE","2","CLOCKWISE","DISPLAY_CYCLE"),
]
CSS="window { background:#0b1020; color:#edf2ff; } .panel { background:#111a2e; border:1px solid #273653; border-radius:14px; padding:12px; } .muted { color:#9aa9c4; } button { background:#1b2943; color:#edf2ff; border:1px solid #354968; border-radius:9px; padding:8px 12px; }"
def run(args):
 try: return subprocess.run(args,text=True,capture_output=True,check=False)
 except OSError: return None
def devices():
 p=run(["xinput","list","--name-only"]); out=["Avtomatik aniqlash"]
 if p and p.returncode==0:
  out += [s.strip() for s in p.stdout.splitlines() if s.strip() and any(k in s.lower() for k in ("touchpad","trackpad","elan","synaptics","clickpad"))]
 return list(dict.fromkeys(out))
class Window(Gtk.Window):
 def __init__(self):
  super().__init__(title="LS Linux Tools"); self.set_default_size(700,650); self.set_border_width(18)
  css=Gtk.CssProvider(); css.load_from_data(CSS.encode()); Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
  root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12); self.add(root)
  head=Gtk.Box(spacing=12); root.pack_start(head,False,False,0)
  logo="/usr/share/icons/hicolor/scalable/apps/ls-linux-tools.svg"
  if Path(logo).exists():
   im=Gtk.Image.new_from_file(logo); im.set_pixel_size(54); head.pack_start(im,False,False,0)
  title=Gtk.Label(); title.set_markup('<span size="xx-large" weight="bold">LS Linux Tools</span>'); title.set_xalign(0); head.pack_start(title,True,True,0)
  card=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); card.get_style_context().add_class("panel"); root.pack_start(card,False,False,0)
  lab=Gtk.Label(label="Sensorli panel qurilmasi"); lab.set_xalign(0); card.pack_start(lab,False,False,0)
  self.device=Gtk.ComboBoxText()
  for d in devices(): self.device.append_text(d)
  self.device.set_active(0); card.pack_start(self.device,False,False,0)
  hint=Gtk.Label(label="Qurilma aniqlanadi. Tanlov diagnostika uchun; Touchégg qurilma filtrlashini har doim qo'llamaydi."); hint.set_xalign(0); hint.set_line_wrap(True); hint.get_style_context().add_class("muted"); card.pack_start(hint,False,False,0)
  self.toggles=[]
  for name,desc,typ,fingers,direction,action in GESTURES:
   row=Gtk.Box(spacing=12); row.get_style_context().add_class("panel"); root.pack_start(row,False,False,0)
   col=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3); row.pack_start(col,True,True,0)
   a=Gtk.Label(label=name); a.set_xalign(0); col.pack_start(a,False,False,0)
   b=Gtk.Label(label=desc); b.set_xalign(0); b.set_line_wrap(True); b.get_style_context().add_class("muted"); col.pack_start(b,False,False,0)
   sw=Gtk.Switch(); sw.set_active(False); sw.set_valign(Gtk.Align.CENTER); row.pack_start(sw,False,False,0); self.toggles.append((sw,typ,fingers,direction,action))
  footer=Gtk.Box(spacing=10); root.pack_end(footer,False,False,0)
  self.status=Gtk.Label(label="O'zgarishlar saqlanmagan"); self.status.set_xalign(0); self.status.set_line_wrap(True); self.status.get_style_context().add_class("muted"); footer.pack_start(self.status,True,True,0)
  btn=Gtk.Button(label="Saqlash va qo'llash"); btn.connect("clicked",self.save); footer.pack_end(btn,False,False,0)
  self.show_all()
 def save(self,*_):
  if not shutil.which("touchegg"):
   self.status.set_text("Touchégg topilmadi: sudo apt install touchegg"); return
  CONFIG.parent.mkdir(parents=True,exist_ok=True)
  root=ET.Element("touchégg",{"name":"Touchegg Configuration","version":"2"})
  app=ET.SubElement(root,"application",{"name":"All"})
  for sw,typ,fingers,direction,action in self.toggles:
   if not sw.get_active(): continue
   node=ET.SubElement(app,"gesture",{"type":typ,"fingers":fingers,"direction":direction})
   if action=="DISPLAY_CYCLE":
    act=ET.SubElement(node,"action",{"type":"COMMAND"}); act.text="/usr/lib/ls-linux-tools/display-cycle"
   else:
    act=ET.SubElement(node,"action",{"type":"SEND_KEYS"}); act.text=action
  ET.indent(root,space="  ")
  tmp=CONFIG.with_suffix(".tmp"); ET.ElementTree(root).write(tmp,encoding="utf-8",xml_declaration=True); tmp.replace(CONFIG)
  run(["systemctl","--user","restart","touchegg"])
  self.status.set_text("Konfiguratsiya saqlandi. Gesture'lar Touchégg versiyasi va X11 muhitiga bog'liq.")
if __name__=="__main__":
 w=Window(); w.connect("destroy",Gtk.main_quit); Gtk.main()
