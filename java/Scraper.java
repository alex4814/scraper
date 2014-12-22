import java.io.*;

import org.jsoup.*;
import org.jsoup.nodes.*;
import org.jsoup.select.*;

import com.gargoylesoftware.htmlunit.*;
import com.gargoylesoftware.htmlunit.html.*;

public class Scraper {
	private static String url_home = "http://guba.eastmoney.com/";
	private static String url_bar = url_home + "list,%d,f_%d.html";
	private static String today = "12-14";

	public void process(String link) throws Exception {
		final WebClient webClient = new WebClient(BrowserVersion.CHROME);
		final HtmlPage html = webClient.getPage(link);

		Document doc = Jsoup.parse(html.asXml());
		Element pager = doc.getElementsByClass("zwhpager").first();
		String url_topic = link.substring(0, link.length() - 5) + "_%d.html";
		int n = Integer.parseInt(pager.getElementsByTag("span").first().text());
		int cnt = 1;
		for (int i = 1; i <= n; ++i) {
			String url = String.format(url_topic, i);
			doc = Jsoup.connect(url).get();
			Elements cmts = doc.getElementsByClass("zwlitxt");
			for (Element cmt : cmts) {
				String name = cmt.getElementsByClass("zwlianame").first().child(0).text();
				String datetime = cmt.getElementsByClass("zwlitime").first().text().substring(4);
				String contents = cmt.getElementsByClass("zwlitext").text();
				System.out.println(cnt++);
				System.out.println(name);
				System.out.println(datetime);
				System.out.println(contents);
				System.out.println();
			}
			break;
		}
		//System.out.println(pager.getElementsByTag("span").first().text());
	}

	public void scrape(int bid) throws Exception {
		int page = 1;
		boolean finish = false;
		while (!finish) {
			String url = String.format(url_bar, bid, page);
			Document doc = Jsoup.connect(url).get();
			Elements tuples = doc.getElementsByClass("articleh");
			for (Element tuple : tuples) {
				String date = tuple.getElementsByClass("l6").first().text();
				Element title = tuple.getElementsByClass("l3").first();
				Element mark = title.getElementsByTag("em").first(); 
				// eliminate top topics
				if (mark != null && mark.hasClass("settop")) {
					continue;
				}
				// process only topics posted after a certain date
				if (date.compareTo(today) < 0) {
					finish = true;
					break;
				}
				String link = title.getElementsByTag("a").first().attr("href");
				process(url_home + link);
			}
			page = page + 1;
		}
	}
	public static void main(String[] args) throws Exception {
		Scraper scraper = new Scraper();
		int bid = 600112;
		scraper.scrape(bid);
		//scraper.process(url_home + "news,gssz,135767483.html");
	}
}

