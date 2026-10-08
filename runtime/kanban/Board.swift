import AppKit
import WebKit

final class BoardApp: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate, NSWindowDelegate {
    var panel: NSPanel!
    var web: WKWebView!
    var timer: Timer?
    var running = false
    var collapsed = false
    var expanded: NSRect = .zero
    let home = FileManager.default.homeDirectoryForCurrentUser
    var resources: URL { Bundle.main.resourceURL! }
    func applicationDidFinishLaunching(_ notification: Notification) {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .nonPersistent()
        config.userContentController.add(self, name: "board")
        web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = self
        let screen = NSScreen.main?.visibleFrame ?? NSRect(x:0,y:0,width:1440,height:900)
        let width = min(720.0, screen.width-24), height = min(480.0,screen.height-24)
        panel = NSPanel(contentRect:NSRect(x:screen.minX+12,y:screen.maxY-height-12,width:width,height:height), styleMask:[.titled,.closable,.miniaturizable,.resizable,.nonactivatingPanel], backing:.buffered, defer:false)
        panel.title = "영상팀 보드 · 표시 전용"
        panel.level = .floating
        panel.hidesOnDeactivate = false
        panel.minSize = NSSize(width:400,height:210)
        panel.isReleasedWhenClosed = false
        panel.delegate = self
        panel.contentView = web
        web.loadFileURL(resources.appendingPathComponent("board.html"), allowingReadAccessTo:resources)
        panel.orderFrontRegardless()
    }
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        refresh()
        timer = Timer.scheduledTimer(withTimeInterval:5,repeats:true) { [weak self] _ in self?.refresh() }
    }
    func refresh() {
        if running { return }; running = true
        let task = Process(), pipe = Pipe(), errors = Pipe()
        task.executableURL = URL(fileURLWithPath:"/usr/bin/python3")
        task.arguments = [resources.appendingPathComponent("snapshot.py").path,"--root",home.appendingPathComponent("Documents/Codex/video-team-runtime").path]
        task.standardOutput = pipe; task.standardError = errors
        do { try task.run() } catch { running=false; web.evaluateJavaScript("window.showError('상태 읽기 프로그램을 시작하지 못했습니다.')");return }
        // Drain while running: never wait on a full stdout pipe on the UI thread.
        DispatchQueue.global(qos:.utility).async { [weak self] in
            let bytes=pipe.fileHandleForReading.readDataToEndOfFile()
            task.waitUntilExit()
            DispatchQueue.main.async {
                guard let self=self else{return}; self.running=false
                guard task.terminationStatus==0, let object=try? JSONSerialization.jsonObject(with:bytes), let safe=try? JSONSerialization.data(withJSONObject:object,options:[.fragmentsAllowed]), let json=String(data:safe,encoding:.utf8) else {self.web.evaluateJavaScript("window.showError('상태 파일 확인 실패 · 이전 표시를 유지합니다.')");return}
                let config=self.home.appendingPathComponent(".codex/video-team-board/selection.json")
                var preferred=""
                if let data=try? Data(contentsOf:config),let value=(try? JSONSerialization.jsonObject(with:data)) as? [String:String] {preferred=value["project"] ?? ""}
                let encoded=String(data:try! JSONSerialization.data(withJSONObject:[preferred]),encoding:.utf8)!
                self.web.evaluateJavaScript("window.updateBoard(\(json),\(encoded)[0])")
            }
        }
    }
    func userContentController(_ userContentController: WKUserContentController,didReceive message: WKScriptMessage) {
        guard let action=message.body as? String else{return}
        if action=="refresh" {refresh()}
        if action=="collapse" {
            if !collapsed {expanded=panel.frame;var small=expanded;small.origin.y += small.height-96;small.size.height=96;panel.minSize=NSSize(width:400,height:96);panel.setFrame(small,display:true)}
            else {panel.setFrame(expanded,display:true);panel.minSize=NSSize(width:400,height:210)}
            collapsed.toggle();web.evaluateJavaScript("document.getElementById('collapse').textContent='\(collapsed ? "펼치기":"접기")'")
        }
    }
    func webView(_ webView:WKWebView,decidePolicyFor navigationAction:WKNavigationAction,decisionHandler:@escaping(WKNavigationActionPolicy)->Void) {decisionHandler(navigationAction.request.url?.isFileURL == true ? .allow : .cancel)}
    func windowWillClose(_ notification: Notification) {timer?.invalidate();NSApp.terminate(nil)}
    func applicationShouldHandleReopen(_ sender:NSApplication,hasVisibleWindows flag:Bool)->Bool {panel.orderFrontRegardless();refresh();return true}
}
let app=NSApplication.shared
let delegate=BoardApp()
app.delegate=delegate
app.setActivationPolicy(.accessory)
app.run()
