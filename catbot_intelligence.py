import nltk
import catunits_catbot
import re
# posts = nltk.corpus.nps_chat.xml_posts()[:10000]
#
names = catunits_catbot.Catunits()
or_ = lambda *words: "(" + "|".join(words) + ")"
atleast = lambda A, B: f"({A}( {B})?|{B})" # matches A, B, or A B
optional = lambda *exprs: "".join(f"({expr} )?" for expr in exprs)
helper_regexes = {
	"name": r"(the )?(?P<name>[\w\s'-]+)",
	"is": or_("is","are"),
	"preposition": or_("on","at","in","as","vs","if","for","with","when","against","compared"),
	"can": or_("(sh|w|c)ould","can","might"),
	"rolled": or_("got","rolled","pulled"),
	"pronoun_other": or_("we","you","yah?",or_("you ","y'?")+or_("all","guys","people","ppl","lot"),"people","ppl","(any|some)?( )?(one|1)( here)?"),
	"pronoun_arbitrary": or_("i","{pronoun_other}"),
	"pronoun_3_singular": or_("he","she","it","that","this"),
	"good": optional("{even}") + or_("{okay}","of any use","any good","an? {okay} " + atleast("({set}|{role})s?","{unit}")),
	"okay": or_("okay","good","great","broken","usable","decent","bad","terrible","awful","trash","garbage"),
	"even": atleast(or_("even","really","actually"),"that"),
	"tierlist": optional(
		or_("a","an","any","the","some"),
		"(sort|kind)( of|a)",
		"(official|community)",
		"({set}|{role})s?",
		"{unit}s?"
	) + "(ranking|tier( )?list)s?",
	"unit": optional("gacha") + atleast(or_(atleast(or_("legend","uber","super","special"),"rare"),"[lusr]r","ex"), "{cat}"),
	"cat": or_(atleast("cat","unit"),"tf", optional("true")+"form"),
	"set": or_(optional("e(lemental)?")+"pixie","luga","(mon(ster)?|g(al(axy)?)?)( )?g(ir|a)l","dark heroe?","dh","ultra soul","us","iron legion","il","almight(y|ie)","dragon( emperor)?","de",atleast(optional("sengoku")+"wargods?","vajira"),"dynamite",atleast("(uber|epic|super)?( )?fest","exclusive"),"neneko","grandon","reinforcement","limited",optional(or_("red","air","floating","metal","wave"))+"bust(er|ing)( exclusive)?"),
	"role": or_(
		or_("anti(-| )?","counter (to|for)")+or_("trait(ed)?","red","floating","black","metal","angel","alien","zombie","relic","traitless","white","aku","coloss(us|al)","baron","beast","behemoth","wave","surge"),
		or_("wave","surge","warp","kb","knockback","freeze","weaken","curse","toxic","poison") + "immune",
		or_("z(ombie)?","witch","eva","coloss(al|us)","beast","behemoth")+"-?(kill|slay)er",
		"(rush|tank|attack)(er)?","snip(er|ing)","range[rd]?","meatshield","ms","melee","(super( )?)?backliner?"
	),
	"um": or_("like","[aeu]+h+m*","[eu]+m+","e+r+")
}
helper_regexes["pronoun_arbitrary"] = helper_regexes["pronoun_arbitrary"].format(**helper_regexes)
helper_regexes["unit"] = helper_regexes["unit"].format(**helper_regexes)
helper_regexes["good"] = helper_regexes["good"].format(**helper_regexes)
helper_regexes["tierlist"] = helper_regexes["tierlist"].format(**helper_regexes)
question_regexes = [
	r"how good {is} {name}(?! {preposition}\b)",
	r"{rolled} (?!.*{rolled}){name}\W? (is {pronoun_3_singular}|are they) {good}( or (what|not?|something|smth))?",
	or_("^",".*"+or_("[^h]ow","[^o]w","[^w]")+" ") + "{is} {name} ?{good}( or (what|not?|something|smth))?",
	r"how (the \w+ )?do(es)? {pronoun_arbitrary} use {name}",
	or_(r"what( (tf|the \w+))?","wt[hf]") + " do(es)? {name} do",
	or_(r"what( (tf|the \w+))?","wt[hf]") + " is {name} used for",
]
question_regexes = [re.compile((r"\b" + r + r"([?\r\n]|$)").replace(" ",r"(\s+({um}\s+)*)").format(**helper_regexes), re.IGNORECASE) for r in question_regexes]

tier_regexes = [
	r"{is} there (still )?{tierlist}",
	r"{pronoun_other} (still )?(have|got) {tierlist}", # optionally add (has|do(es)?|{pronoun_other} know if) in front
	r"(where|how) ({pronoun_arbitrary} {can}|{can} {pronoun_arbitrary}) (be able to )?(find|get|see|look at|obtain|access|(obtain|get) access to) {tierlist}",
	r"where('?s| ((tf|the \w+) )?{is}) {tierlist}",
	r"what {tierlist} ({is} there|(to|{can} {pronoun_arbitrary}) use)"
]
tier_regexes = [re.compile((r"(^|[^`'\x22])\b" + r + r"\b($|[^`'\x22])").replace(" ",r"(\s+({um}\s+)*)").format(**helper_regexes), re.IGNORECASE) for r in tier_regexes]


def is_unit_question_regex(message, errors=0):
	for regex in question_regexes:
		regex_extracted = regex.search(message)
		if regex_extracted is None: continue
		name = regex_extracted.group('name').strip()

		if name.isdigit(): continue
		if name.lower() == "god": continue

		for n in [name, f"the {name}"]:
			unit_to_search = names.getUnitCode(n, errors)[0]
			if unit_to_search not in ['no result', 'name not unique']:
				return names.getnamebycode(unit_to_search)
	return ''

def is_tier_list_question(message):
	for regex in tier_regexes:
		regex_extracted = regex.search(message)
		if regex_extracted is not None:
			return True
	return False
