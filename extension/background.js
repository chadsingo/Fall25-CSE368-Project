function handleUpdated(tabId, changeInfo, tabInfo) {
    if ((tabInfo["url"].match("https:\\/\\/piazza\\.com\\/class\\/.*\\/post\\/.*")).length > 0 && tabInfo["status"] === "complete") {
        console.log("Sent message to tab "+tabId+" ("+tabInfo["url"]+")")
        if (chrome) {
            chrome.tabs.sendMessage(tabId, {"load": "the thing"})
        } else {
            browser.tabs.sendMessage(tabId, {"load": "the thing"})
        }
    }
}

if (chrome) {
    chrome.tabs.onUpdated.addListener(
        handleUpdated
    );
} else {
    browser.tabs.onUpdated.addListener(
        handleUpdated,
        {
            "properties": ["status"],
            "urls": ["*://piazza.com/class/*/post/*"]
        }
    );
}
