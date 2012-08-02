/*
 * jquery.password.js
 * Copyright(c) 2011 设计蜂巢
	* version: 1.0
 * Date: 2011-10-18 16:38:34
	* Description: 密码强度验证代码，部分代码提取自：https://twitter.com/signup
	*	callback：{isValid:true/false,tipClass:string,score:number}
 * Blog: http://www.hujuntao.com/
 * Update: http://code.google.com/p/hujuntao/
 */
(function ($) {
    $.fn.extend({
        password: function (options) {
            var defualts = {
                val: $(this).val(),
                score: $('.score b'),
                banned: ["000000", "111111", "11111111", "112233", "121212", "123123", "123456", "1234567", "12345678", "123456789", "131313", "232323", "654321", "666666", "696969", "777777", "7777777", "8675309", "987654", "nnnnnn", "nop123", "nop123", "nopqrs", "noteglh", "npprff", "npprff14", "npgvba", "nyoreg", "nyoregb", "nyrkvf", "nyrwnaqen", "nyrwnaqeb", "nznaqn", "nzngrhe", "nzrevpn", "naqern", "naqerj", "natryn", "natryf", "navzny", "nagubal", "ncbyyb", "nccyrf", "nefrany", "neguhe", "nfqstu", "nfqstu", "nfuyrl", "nffubyr", "nhthfg", "nhfgva", "onqobl", "onvyrl", "onanan", "onearl", "onfronyy", "ongzna", "orngevm", "ornire", "ornivf", "ovtpbpx", "ovtqnqql", "ovtqvpx", "ovtqbt", "ovtgvgf", "oveqvr", "ovgpurf", "ovgrzr", "oynmre", "oybaqr", "oybaqrf", "oybjwbo", "oybjzr", "obaq007", "obavgn", "obaavr", "obbobb", "obbtre", "obbzre", "obfgba", "oenaqba", "oenaql", "oenirf", "oenmvy", "oebapb", "oebapbf", "ohyyqbt", "ohfgre", "ohggre", "ohggurnq", "pnyiva", "pnzneb", "pnzreba", "pnanqn", "pncgnva", "pneybf", "pnegre", "pnfcre", "puneyrf", "puneyvr", "purrfr", "puryfrn", "purfgre", "puvpntb", "puvpxra", "pbpnpbyn", "pbssrr", "pbyyrtr", "pbzcnd", "pbzchgre", "pbafhzre", "pbbxvr", "pbbcre", "pbeirggr", "pbjobl", "pbjoblf", "pelfgny", "phzzvat", "phzfubg", "qnxbgn", "qnyynf", "qnavry", "qnavryyr", "qroovr", "qraavf", "qvnoyb", "qvnzbaq", "qbpgbe", "qbttvr", "qbycuva", "qbycuvaf", "qbanyq", "qentba", "qernzf", "qevire", "rntyr1", "rntyrf", "rqjneq", "rvafgrva", "rebgvp", "rfgeryyn", "rkgerzr", "snypba", "sraqre", "sreenev", "sveroveq", "svfuvat", "sybevqn", "sybjre", "sylref", "sbbgonyy", "sberire", "serqql", "serrqbz", "shpxrq", "shpxre", "shpxvat", "shpxzr", "shpxlbh", "tnaqnys", "tngrjnl", "tngbef", "trzvav", "trbetr", "tvnagf", "tvatre", "tvmzbqb", "tbyqra", "tbysre", "tbeqba", "tertbel", "thvgne", "thaare", "unzzre", "unaanu", "uneqpber", "uneyrl", "urngure", "uryczr", "uragnv", "ubpxrl", "ubbgref", "ubearl", "ubgqbt", "uhagre", "uhagvat", "vprzna", "vybirlbh", "vagrearg", "vjnagh", "wnpxvr", "wnpxfba", "wnthne", "wnfzvar", "wnfcre", "wraavsre", "wrerzl", "wrffvpn", "wbuaal", "wbuafba", "wbeqna", "wbfrcu", "wbfuhn", "whavbe", "whfgva", "xvyyre", "xavtug", "ynqvrf", "ynxref", "ynhera", "yrngure", "yrtraq", "yrgzrva", "yrgzrva", "yvggyr", "ybaqba", "ybiref", "znqqbt", "znqvfba", "znttvr", "zntahz", "znevar", "znevcbfn", "zneyobeb", "znegva", "zneiva", "znfgre", "zngevk", "znggurj", "znirevpx", "znkjryy", "zryvffn", "zrzore", "zreprqrf", "zreyva", "zvpunry", "zvpuryyr", "zvpxrl", "zvqavtug", "zvyyre", "zvfgerff", "zbavpn", "zbaxrl", "zbaxrl", "zbafgre", "zbetna", "zbgure", "zbhagnva", "zhssva", "zhecul", "zhfgnat", "anxrq", "anfpne", "anguna", "anhtugl", "app1701", "arjlbex", "avpubynf", "avpbyr", "avccyr", "avccyrf", "byvire", "benatr", "cnpxref", "cnagure", "cnagvrf", "cnexre", "cnffjbeq", "cnffjbeq", "cnffjbeq1", "cnffjbeq12", "cnffjbeq123", "cngevpx", "crnpurf", "crnahg", "crccre", "cunagbz", "cubravk", "cynlre", "cyrnfr", "cbbxvr", "cbefpur", "cevapr", "cevaprff", "cevingr", "checyr", "chffvrf", "dnmjfk", "djregl", "djreglhv", "enoovg", "enpury", "enpvat", "envqref", "envaobj", "enatre", "enatref", "erorppn", "erqfxvaf", "erqfbk", "erqjvatf", "evpuneq", "eboreg", "eboregb", "ebpxrg", "ebfrohq", "ehaare", "ehfu2112", "ehffvn", "fnznagun", "fnzzl", "fnzfba", "fnaqen", "fnghea", "fpbbol", "fpbbgre", "fpbecvb", "fpbecvba", "fronfgvna", "frperg", "frkfrk", "funqbj", "funaaba", "funirq", "fvreen", "fvyire", "fxvccl", "fynlre", "fzbxrl", "fabbcl", "fbppre", "fbcuvr", "fcnaxl", "fcnexl", "fcvqre", "fdhveg", "fevavinf", "fgnegerx", "fgnejnef", "fgrryref", "fgrira", "fgvpxl", "fghcvq", "fhpprff", "fhpxvg", "fhzzre", "fhafuvar", "fhcrezna", "fhesre", "fjvzzvat", "flqarl", "grdhvreb", "gnlybe", "graavf", "grerfn", "grfgre", "grfgvat", "gurzna", "gubznf", "guhaqre", "guk1138", "gvssnal", "gvtref", "gvttre", "gbzpng", "gbctha", "gblbgn", "genivf", "gebhoyr", "gehfgab1", "ghpxre", "ghegyr", "gjvggre", "havgrq", "intvan", "ivpgbe", "ivpgbevn", "ivxvat", "ibbqbb", "iblntre", "jnygre", "jneevbe", "jrypbzr", "jungrire", "jvyyvnz", "jvyyvr", "jvyfba", "jvaare", "jvafgba", "jvagre", "jvmneq", "knivre", "kkkkkk", "kkkkkkkk", "lnznun", "lnaxrr", "lnaxrrf", "lryybj", "mkpioa", "mkpioaz", "mmmmmm"],
                minChar: 6,
                username: '',
                callback: function () {},
                requireStrong: false
            };
            var opts = $.extend({}, defualts, options);
												/*重复字符检测*/
            function repeat(F, I) {
                var E = "";
                for (var H = 0; H < I.length; H++) {
                    var J = true;
                    for (var G = 0; G < F && (G + H + F) < I.length; G++) {
                        J = J && (I.charAt(G + H) == I.charAt(G + H + F))
                    }
                    if (G < F) {
                        J = false
                    }
                    if (J) {
                        H += F - 1;
                        J = false
                    } else {
                        E += I.charAt(H)
                    }
                }
                return E
            }

            function strength() {
                var K = 0;
                /*密码长度检测*/
                if (opts.val.length < (opts.minChar || 6)) {
                    return {
                        score: 0,
                        msgClass: "tooshort"
                    }
                }
																/*空白符检测*/
                if (/\s/.test(opts.val)) {
                    return {
                        score: 0,
                        msgClass: "whitespace"
                    }
                }
                var J = opts.val.toLowerCase(); 
																/*检测密码是否和用户名相同*/
                if (opts.username && J == ($.isFunction(F.username) ? F.username() : F.username).toLowerCase()) {
                    return {
                        score: 0,
                        msgClass: "obvious"
                    }
                }
																/*禁止密码检测*/
                if ($.inArray(J, opts.banned || []) != -1) {
                    return {
                        score: 0,
                        msgClass: "banned"
                    }
                }
																/*强密码检测模式*/
                if (opts.requireStrong) {
                    var E = "# ` ~ ! @ $ % ^ & * ( ) - _ = + [ ] { } | ; : ' \" , . < > / ?".split(" ");
                    E = $.map(E, function (L) {
                        return "\\" + L
                    }).join("");
                    var H = ["\\d", "[a-z]", "[A-Z]", "[" + E + "]"];
                    var I = $.map(H, function (L) {
                        return "(?=.*" + L + ")"
                    }).join("");
                    if (!new RegExp("(" + I + "){10,}").test(opts.val)) {
                        return {
                            score: 0,
                            msgClass: "tooweak"
                        }
                    }
                }
                K += opts.val.length * 4;
                K += (repeat(1, opts.val).length - opts.val.length) * 1;
                K += (repeat(2, opts.val).length - opts.val.length) * 1;
                K += (repeat(3, opts.val).length - opts.val.length) * 1;
                K += (repeat(4, opts.val).length - opts.val.length) * 1;
                if (/(.*[0-9].*[0-9].*[0-9])/.test(opts.val)) {
                    K += 5
                }
                if (/(.*[!@#$%^&*?_~].*[!@#$%^&*?_~])/.test(opts.val)) {
                    K += 5
                }
                if (/([a-z].*[A-Z])|([A-Z].*[a-z])/.test(opts.val)) {
                    K += 10
                }
                if (/([a-zA-Z])/.test(/([a-zA-Z])/) && /([0-9])/.test(opts.val)) {
                    K += 15
                }
                if (/([!@#$%^&*?_~])/.test() && /([0-9])/.test(opts.val)) {
                    K += 15
                }
                if (/([!@#$%^&*?_~])/.test(opts.val) && /([a-zA-Z])/.test(opts.val)) {
                    K += 15
                }
                if (/^\w+$/.test(opts.val) || /^\d+$/.test(opts.val)) {
                    K -= 10
                }
                if (K < 0) {
                    K = 0
                }
                if (K > 100) {
                    K = 100
                }
                if (K < 34) {
                    return {
                        score: K,
                        msgClass: "weak"
                    }
                }
                if (K < 50) {
                    return {
                        score: K,
                        msgClass: "good"
                    }
                }
                if (K < 75) {
                    return {
                        score: K,
                        msgClass: "strong"
                    }
                }
                return {
                    score: K,
                    msgClass: "verystrong"
                }
            }
            var W = {
                isValid: !/\s/.test(opts.val),
                tipClass: "tip"
            },
                Y = strength();
            if (!Y.score) {
                W.isValid = false
            }
            switch (Y.msgClass) {
            case "obvious":
            case "banned":
                W.tipClass = "obvious";
                break;
            case "whitespace":
            case "tooshort":
            case "tooweak":
                W.tipClass = "invalid";
                break;
            case "verystrong":
                W.tipClass = "perfect";
                break;
            case "good":
            case "strong":
                W.tipClass = "ok";
                break;
            case "weak":
            default:
                W.tipClass = "weak." + (Y.score > 9 ? "isaok" : "error");
                break
            }
            $(opts.score).fadeIn().animate({
                width: (Y.score / 2)
            })
            $('.' + W.tipClass).addClass('active').siblings().removeClass('active');
            opts.callback(W.isValid, W.tipClass, Y.score)
        }
    })
})(jQuery);