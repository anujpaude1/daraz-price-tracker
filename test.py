from main import user_data, fetch_price

gg=fetch_price("https://www.daraz.com.np/products/4-in-1-fast-charging-cable-type-cusb-alightning-dual-type-c-pd-27w-65w-nylon-braided-cable-flat-braided-i-phone-charging-cable-with-velcro-multi-charging-cable-combo-type-cusb-a-ports-i159605792-s1143266530.html?scm=1007.51657.380827.0&pvid=b305d097-de6f-4561-a1fb-eeaccedb9f56&search=flashsale&spm=a2a0e.tm80335409.FlashSale.d_159605792")  # Example product link

print(gg)
fetch("https://acs-m.daraz.com.np/h5/mtop.global.detail.web.getdetailinfo/1.0/?jsv=2.6.1&appKey=24937400&t=1734758183390&sign=97b18bb965cd6d5560f3c705ef7bf956&api=mtop.global.detail.web.getDetailInfo&v=1.0&type=originaljson&isSec=1&AntiCreep=true&timeout=20000&dataType=json&sessionOption=AutoLoginOnly&x-i18n-language=en&x-i18n-regionID=NP&traffic=drz-replatform", {
  "headers": {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.6",
    "content-type": "application/x-www-form-urlencoded",
    "entrance": "",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Brave\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "traffic": "drz-replatform",
    "x-i18n-language": "en",
    "x-i18n-regionid": "NP"
  },
  "referrer": "https://www.daraz.com.np/",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "data=%7B%22deviceType%22%3A%22android%22%2C%22path%22%3A%22https%3A%2F%2Fwww.daraz.com.np%2Fproducts%2Fstylish-trending-printed-double-sided-premium-shawl-winter-scarf-for-women-i129162051-s1037174434.html%3F%26scm%3D1007.51657.380827.0%26pvid%3D565daa7b-0000-4fdf-bd06-cec5b4cb1684%26search%3Dflashsale%3Fsearch%3D1%26mp%3D1%26c%3Dfs%26clickTrackInfo%3Drs%253A0.336%253Bfs_item_discount_price%253A649%253Bitem_id%253A129162051%253Bpctr%253A0.0%253Bcalib_pctr%253A0.0%253Bvoucher_price%253A649%253Bmt%253Amustbuy%253Bpromo_price%253A649%253Bfs_utdid%253A-1%253Bfs_item_sold_cnt%253A8%253Babid%253A380827%253Bfs_item_price%253A1499%253Bpvid%253A565daa7b-0000-4fdf-bd06-cec5b4cb1684%253Bfs_min_price_l30d%253A0%253Bdata_type%253Aflashsale%253Bfs_pvid%253A565daa7b-0000-4fdf-bd06-cec5b4cb1684%253Btime%253A1734758151%253Bfs_biz_type%253Afs%253Bscm%253A1007.51657.380827.%253Bchannel_id%253A0000%253Bfs_item_discount%253A57%2525%253Bcampaign_id%253A307838%26scm%3D1007.51657.380827.0%22%2C%22uri%22%3A%22stylish-trending-printed-double-sided-premium-shawl-winter-scarf-for-women-i129162051-s1037174434%22%2C%22headerParams%22%3A%22%7B%5C%22user-agent%5C%22%3A%5C%22Mozilla%2F5.0%20(Linux%3B%20Android%206.0%3B%20Nexus%205%20Build%2FMRA58N)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Mobile%20Safari%2F537.36%5C%22%7D%22%2C%22cookieParams%22%3A%22%7B%5C%22__wpkreporterwid_%5C%22%3A%5C%22b8ea80ce-fb65-4881-2c95-4a3d82daab5a%5C%22%2C%5C%22hng%5C%22%3A%5C%22NP%7Cen-NP%7CNPR%7C524%5C%22%2C%5C%22hng.sig%5C%22%3A%5C%22CpTPf0oy-Ji7yHXlTqu1ZBr2yy4DEw3ATHLSHmIgtyk%5C%22%2C%5C%22lzd_cid%5C%22%3A%5C%222ff2768d-8922-431c-bdc2-fe5e3b8dc9ae%5C%22%2C%5C%22t_fv%5C%22%3A%5C%221734750358962%5C%22%2C%5C%22t_uid%5C%22%3A%5C%22i7gl6AQHuMIecQJYbOAykClJxAXODhGk%5C%22%2C%5C%22lwrid%5C%22%3A%5C%22AgGT5y3On%252BVR4kEUKb%252FQX39uI2BR%5C%22%2C%5C%22_m_h5_tk%5C%22%3A%5C%229b8a8000c714538cc5d8b3ea915fb170_1734760440038%5C%22%2C%5C%22_m_h5_tk_enc%5C%22%3A%5C%222fafc987bb503eb755dffb00b7f9d08a%5C%22%2C%5C%22lwrtk%5C%22%3A%5C%22AAEEZ2ahFwQ4MKMMfSQpmpRLO7FKZTn8urvFVM3Fdhdh1pI%2FQ1snFgU%5C%22%2C%5C%22t_sid%5C%22%3A%5C%22xGpa33jVZzl5Y3R1QZX0B9u32nTpbVBh%5C%22%2C%5C%22utm_channel%5C%22%3A%5C%22NA%5C%22%2C%5C%22__itrace_wid%5C%22%3A%5C%22d4ed8f96-fa9c-4f81-0acd-af0df5274c31%5C%22%2C%5C%22G_ENABLED_IDPS%5C%22%3A%5C%22google%5C%22%2C%5C%22epssw%5C%22%3A%5C%227*Kppss6E9AE86ceDLsE3vv28as0nOnIhMkgmn9t1KdiCB58lOV--EPtO_hJIb463sswGG7gd3ssg1REzsss3vTass7UDsSsdrq3IyvsMo7C08nFYsj0eSI28vug3sfuKzaTb5zd2XbK1LmLBAjrwQqtgijNjaOfm5C0YW0oAiw71iKv31NBcSgPUyOF3ZLRHOuczS3BcPeD2jo9UjByEk36EsWn3m-XVdaLdJc1KuKPgEIyMSY7DjGf1EYJ2y_ZtamuDmSijKf1ftcxOtC0Vl-WbM8Iass3hhbq3R90Ci4Qwh9nnM7MysT_Z7ffYsss0AIWzsRE4V9RDLqyB7CD6hGGShRl0Ansus78MJgG_Vx0F.%5C%22%2C%5C%22tfstk%5C%22%3A%5C%22gOWqnr65N-eqnKX4S3vZUaaExS9vHK4CoOT6jGjMcEYmhxgGawQwfoh1jF7NPUO65K4qbGY5RdZvlO6ySN_lGNSTDhYGSN81G7wCDip9Iy1adJsxPctUpZRmIYqMjnDgVIYD7KBXIyaQd8TwcAJGl19Yg7SkyhkDjdbiqYxHrncDmNYkZHxIodvGSuRkxHMMjCADZ0xXrFvMINju4hHHpFTQ_hd0v7eVVwDUeIYhmUkiL4K2igyprADGUnSyyiVrIAXy0IX6PE0roI1GvBBfnRkJhM5kE3B_yxYNZHS6UOzxhFpDvBCBaqqvc1jRsEBU7v8cH_WwF94tdw7fr991nlGP-C8VZtArjAvW3_7N_p0u2n1G21YALPkeotIPOC5Y8XQhVM6vwOzErFCXvLxRCzHD7_xG4Z39qu8ABuGE_IxJ4eZz4to8SsEladuj6fdfa38Qm2ct6Ixp4eZz2fh9G_-yRo0h.%5C%22%2C%5C%22isg%5C%22%3A%5C%22BPT0KhplL0FFwLpLRIpIdCJ5xbJmzRi3PO0Un45V2X8o-ZVDtt1RRiqxfSkhAVAP%5C%22%7D%22%2C%22requestParams%22%3A%22%7B%5C%22scm%5C%22%3A%5C%221007.51657.380827.0%5C%22%2C%5C%22pvid%5C%22%3A%5C%22565daa7b-0000-4fdf-bd06-cec5b4cb1684%5C%22%2C%5C%22search%5C%22%3A%5C%22flashsale%3Fsearch%3D1%5C%22%2C%5C%22mp%5C%22%3A%5C%221%5C%22%2C%5C%22c%5C%22%3A%5C%22fs%5C%22%2C%5C%22clickTrackInfo%5C%22%3A%5C%22rs%3A0.336%3Bfs_item_discount_price%3A649%3Bitem_id%3A129162051%3Bpctr%3A0.0%3Bcalib_pctr%3A0.0%3Bvoucher_price%3A649%3Bmt%3Amustbuy%3Bpromo_price%3A649%3Bfs_utdid%3A-1%3Bfs_item_sold_cnt%3A8%3Babid%3A380827%3Bfs_item_price%3A1499%3Bpvid%3A565daa7b-0000-4fdf-bd06-cec5b4cb1684%3Bfs_min_price_l30d%3A0%3Bdata_type%3Aflashsale%3Bfs_pvid%3A565daa7b-0000-4fdf-bd06-cec5b4cb1684%3Btime%3A1734758151%3Bfs_biz_type%3Afs%3Bscm%3A1007.51657.380827.%3Bchannel_id%3A0000%3Bfs_item_discount%3A57%25%3Bcampaign_id%3A307838%5C%22%7D%22%7D",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});