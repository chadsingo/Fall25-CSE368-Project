function handleUpdated(tabId, changeInfo, tabInfo) {
    if ((tabInfo["url"].match("https:\\/\\/piazza\\.com\\/class\\/.*\\/post\\/.*")).length > 0 && tabInfo["status"] === "complete") {
        console.log("Sent message to tab "+tabId+" ("+tabInfo["url"]+")")
        browser.tabs.sendMessage(tabId, {"load": "the thing"})
    }
}

browser.tabs.onUpdated.addListener(
    handleUpdated,
    {
        "properties": ["status"],
        "urls": ["*://piazza.com/class/*/post/*"]
    }
);