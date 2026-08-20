from typing import Dict, Any, Optional

DENTAL_EDUCATIONAL_ENCYCLOPEDIA = {
    'dental-filling': {
        'keywords': ['filling', 'fillings', 'cavity', 'cavities', 'decay', 'hole in tooth', 'दाँत भर्ने', 'दाँत भर्ने सेवा', 'कम्पोजिट फिलिङ'],
        'en': {
            'title': 'Dental Filling (Tooth-Colored Restorations)',
            'definition': (
                "A **Dental Filling** is a restorative dental treatment used to repair and rebuild a tooth that has been damaged by decay (a cavity), erosion, or minor fractures. "
                "The goal of a filling is to remove bacteria, seal the compromised space, and restore the tooth's original strength, shape, and chewing function so it looks and feels completely natural."
            ),
            'how_it_works': (
                "**How the Dental Filling Procedure Works (Step-by-Step):**\n"
                "1. **Gentle Preparation & Numbing:** The area around the tooth is comfortably numbed with local anesthesia so you feel zero pain.\n"
                "2. **Decay Removal & Sanitization:** The dentist gently cleans away the decayed enamel/dentin and sanitizes the area to eliminate all bacteria.\n"
                "3. **Etching & Bonding Adhesive:** A special conditioning gel is applied to create microscopic anchor points, followed by a dental adhesive.\n"
                "4. **Composite Resin Placement:** Biocompatible, tooth-colored composite resin is carefully layered into the cavity and shaped to match the natural anatomy of your tooth.\n"
                "5. **LED Light Curing:** A high-intensity blue LED light hardens the composite material in seconds.\n"
                "6. **Bite Check & High-Shine Polish:** The dentist checks your bite and polishes the filling smooth so it seamlessly blends with your surrounding teeth."
            ),
            'benefits': (
                "💡 **Why Dental Fillings are Essential:**\n"
                "• **Stops Infection Early:** Prevents decay from reaching the tooth's inner pulp (which would require a Root Canal Treatment or extraction).\n"
                "• **Painless & Quick:** Most fillings are completed in just 30 to 45 minutes.\n"
                "• **Invisible Aesthetics:** Modern composite resin matches the exact natural shade of your enamel."
            )
        },
        'ne': {
            'title': 'दाँत भर्ने सेवा (Dental Filling / Composite Restoration)',
            'definition': (
                "**दाँत भर्ने (Dental Filling)** भनेको किरा लागेको (क्याभिटी भएको), फुटेको वा खिइएको दाँतलाई सफा गरी दाँतकै रङको विशेष बायो-कम्प्याटिबल सामग्रीले भरेर पहिले जस्तै बलियो र सुन्दर बनाउने उपचार विधि हो। "
                "यसले ब्याक्टेरियालाई भित्र पस्नबाट रोक्छ र दाँतको प्राकृतिक चपाउने शक्ति फर्काउँछ।"
            ),
            'how_it_works': (
                "**दाँत भर्ने प्रक्रिया (Step-by-Step):**\n"
                "१. **दुखाइरहित तयारी:** स्थानीय एनेस्थेसिया दिएर दाँतको भागलाई पूर्ण रूपमा दुखाइमुक्त बनाइन्छ।\n"
                "२. **किरा लागेको भागको सफाइ:** दाँतमा किरा लागेको कालो वा बिग्रेको भागलाई सफा गरी जीवाणुरहित बनाइन्छ।\n"
                "३. **बन्डिङ र कम्पोजिट लेयरिङ:** दाँतकै रङसँग मिल्ने उच्च गुणस्तरको कम्पोजिट रेजिन सामग्री खाडलमा मिलाएर भरिन्छ।\n"
                "४. **एलईडी लाइटद्वारा कडा बनाउने:** विशेष निलो एलईडी लाइटको सहायताले उक्त मसलालाई केही सेकेन्डमै बलियो बनाइन्छ।\n"
                "५. **पोलिसिङ:** दाँतको टोकाइ मिलाएर प्राकृतिक दाँत जस्तै चम्किलो र चिल्लो बनाइन्छ।"
            ),
            'benefits': (
                "💡 **दाँत समयमै भर्नुका फाइदाहरू:**\n"
                "• किरालाई दाँतको नशासम्म पुग्नबाट रोक्छ (जसले गर्दा पछि रूट क्यानल वा दाँत निकाल्नु पर्दैन)।\n"
                "• मात्र ३०–४५ मिनेटमै उपचार सम्पन्न हुन्छ।\n"
                "• प्राकृतिक दाँत जस्तै देखिन्छ, अरूले भरेको थाहा पाउँदैनन्।"
            )
        }
    },
    'root-canal-treatment': {
        'keywords': ['rct', 'root canal', 'root canal treatment', 'nerve treatment', 'pulp', 'रूट क्यानल', 'रुट क्यानल', 'नशाको उपचार'],
        'en': {
            'title': 'Root Canal Treatment (RCT)',
            'definition': (
                "A **Root Canal Treatment (RCT)** is a specialized endodontic procedure performed to save and repair a severely infected or badly decayed tooth rather than pulling it out. "
                "When decay or injury reaches the soft inner core of the tooth (the dental pulp containing nerves and blood vessels), it causes intense throbbing pain and abscesses. RCT removes the infected pulp, sanitizes the internal canals, and seals the tooth permanently."
            ),
            'how_it_works': (
                "**How a Root Canal Treatment is Performed:**\n"
                "1. **Comfortable Local Numbing:** Profound local anesthesia ensures the entire procedure is completely painless.\n"
                "2. **Accessing the Pulp:** A tiny microscopic opening is created on the biting surface of the tooth.\n"
                "3. **Cleaning & Shaping Canals:** Specialized rotary instruments gently remove the infected pulp and nerve tissue, and the canals are disinfected with antibacterial solutions.\n"
                "4. **Biocompatible Sealing (Gutta-Percha):** The root canals are hermetically sealed with a rubber-like biocompatible material called Gutta-Percha to prevent reinfection.\n"
                "5. **Crown Placement:** A dental crown (cap) is placed over the treated tooth to protect it from fracturing and restore full chewing strength."
            ),
            'benefits': (
                "💡 **Is RCT Painful?**\n"
                "No! With modern rotary technology and precise digital anesthesia at CareFirst, getting an RCT is as comfortable and painless as receiving a standard filling."
            )
        },
        'ne': {
            'title': 'रूट क्यानल उपचार (Root Canal Treatment - RCT)',
            'definition': (
                "**रूट क्यानल उपचार (RCT)** भनेको दाँतको भित्री नशा (Pulp) सम्म किरा वा संक्रमण पुगेर असह्य दुखाइ हुँदा, दाँत ननिकाली भित्रको नशा सफा गरेर दाँतलाई सधैंका लागि जोगाउने आधुनिक दन्त शल्यक्रिया विधि हो।"
            ),
            'how_it_works': (
                "**रूट क्यानल उपचार प्रक्रिया:**\n"
                "१. **एनेस्थेसिया:** दाँतलाई पूर्ण रूपमा लाटो बनाएर दुखाइरहित बनाइन्छ।\n"
                "२. **संक्रमित नशाको सफाइ:** रोटरी यन्त्रको मद्दतले दाँतको जराभित्र रहेका सबै बिग्रिएका नशा र ब्याक्टेरिया पूर्ण रूपमा निकालिन्छ।\n"
                "३. **जीवाणुरहित सिलिङ:** सफा गरिएको जराको नलीलाई विशेष गट्टा-पर्चा (Gutta-Percha) ले सधैंका लागि सिल गरिन्छ।\n"
                "४. **क्याप (Crown) लगाउने:** दाँतलाई फुट्नबाट जोगाउन र पहिले जस्तै बलियो बनाउन माथिबाट सिर्यामिक क्याप लगाइन्छ।"
            ),
            'benefits': (
                "💡 **के RCT गर्दा दुख्छ?**\n"
                "नाइँ! केयरफर्स्टमा आधुनिक एनेस्थेसिया र कम्प्युटर प्रविधिबाट गरिने भएकाले रूट क्यानल गर्दा कुनै दुखाइ हुँदैन।"
            )
        }
    },
    'dental-implants': {
        'keywords': ['implant', 'implants', 'dental implant', 'tooth implant', 'इम्प्लान्ट', 'दाँत प्रत्यारोपण'],
        'en': {
            'title': 'Dental Implants (Permanent Tooth Replacement)',
            'definition': (
                "A **Dental Implant** is the gold-standard, most permanent solution for replacing missing teeth. "
                "It consists of a surgical-grade titanium post placed directly into the jawbone to act as an artificial root, onto which a custom ceramic tooth crown is permanently anchored."
            ),
            'how_it_works': (
                "**How the Dental Implant Process Works:**\n"
                "1. **3D Digital Planning:** 3D CBCT imaging evaluates your jawbone density and maps the optimal implant location.\n"
                "2. **Precision Titanium Placement:** The titanium implant screw is placed into the bone with gentle local numbing.\n"
                "3. **Osseointegration (Healing):** Over 3 to 6 months, the implant fuses permanently with your natural jawbone tissue.\n"
                "4. **Custom Ceramic Crown:** A lifelike zirconia or ceramic crown is attached to match your natural smile perfectly."
            ),
            'benefits': (
                "💡 **Key Advantages of Implants:**\n"
                "• **Lasts a Lifetime:** 98%+ clinical success rate.\n"
                "• **Preserves Jawbone:** Prevents bone loss and facial sagging.\n"
                "• **No damage to neighboring teeth:** Unlike bridges, nearby teeth remain untouched."
            )
        },
        'ne': {
            'title': 'डेन्टल इम्प्लान्ट (Dental Implants - स्थायी दाँत प्रत्यारोपण)',
            'definition': (
                "**डेन्टल इम्प्लान्ट** भनेको झरेको वा निकालिएको दाँतको ठाउँमा प्राकृतिक दाँत जस्तै जरासहित नयाँ दाँत बसाउने सबैभन्दा आधुनिक र स्थायी विधि हो। "
                "यसमा टाइटेनियमको जरा बङ्गराको हड्डीमा राखिन्छ र माथिबाट प्राकृतिक दाँत जस्तै देखिने क्याप लगाइन्छ।"
            ),
            'how_it_works': (
                "**इम्प्लान्ट प्रक्रिया:**\n"
                "१. थ्रीडी डिजिटल एक्स-रेबाट हड्डीको अवस्था जाँच गरिन्छ।\n"
                "२. दुखाइरहित तरिकाले टाइटेनियमको इम्प्लान्ट हड्डीमा प्रत्यारोपण गरिन्छ।\n"
                "३. हड्डीसँग इम्प्लान्ट प्राकृतिक रूपमा जोडिएपछि माथिबाट सिर्यामिक क्याप लगाइन्छ।"
            ),
            'benefits': (
                "💡 **इम्प्लान्टका फाइदाहरू:**\n"
                "• जीवनभर टिक्ने स्थायी समाधान।\n"
                "• प्राकृतिक दाँत जस्तै बलियो र चपाउन सहज।\n"
                "• दायाँबायाँका अन्य दाँतलाई कुनै असर गर्दैन।"
            )
        }
    },
    'orthodontic-treatment-braces': {
        'keywords': ['braces', 'aligner', 'aligners', 'orthodontics', 'crooked teeth', 'teeth wire', 'तार बाँध्ने', 'ब्रेसेस'],
        'en': {
            'title': 'Orthodontic Treatment (Braces & Clear Aligners)',
            'definition': (
                "**Orthodontic Treatment** focuses on straightening crooked, crowded, or protruding teeth and correcting irregular bites (such as overbites, underbites, or crossbites). "
                "It improves both facial aesthetics and your ability to chew, speak, and maintain long-term oral hygiene."
            ),
            'how_it_works': (
                "**Treatment Options:**\n"
                "• **Metal / Ceramic Braces:** Brackets and high-tech archwires apply gentle, continuous pressure to guide teeth into perfect alignment.\n"
                "• **Clear Invisible Aligners:** Custom series of transparent, removable aligner trays that straighten teeth discreetly without visible wires.\n"
                "• **Treatment Duration:** Typically spans 12 to 18 months with monthly checkups."
            ),
            'benefits': (
                "💡 Straight teeth are significantly easier to clean, preventing cavities, gum disease, and uneven tooth wear."
            )
        },
        'ne': {
            'title': 'तार बाँध्ने सेवा (Orthodontic Braces & Clear Aligners)',
            'definition': (
                "**अर्थोडोन्टिक उपचार (तार बाँध्ने / ब्रेसेस)** भनेको बाङ्गो, टिङ्गो, खप्टिएको वा फाटिएको दाँतलाई मिलाएर आकर्षक र मिलेको मुस्कान बनाउने उपचार हो।"
            ),
            'how_it_works': (
                "**उपलब्ध विकल्पहरू:**\n"
                "• **मेटल तथा सिर्यामिक ब्रेसेस:** दाँतमा स-साना ब्राकेट र तार जोडेर दाँतलाई सही ठाउँमा ल्याइन्छ।\n"
                "• **पारदर्शी अलाइनर (Clear Aligners):** नदेखिने पारदर्शी कभर लगाएर दाँत मिलाइन्छ।\n"
                "• **समय अवधि:** सामान्यतया १२ देखि १८ महिना।"
            ),
            'benefits': (
                "💡 मिलेको दाँतले अनुहारको सुन्दरता बढाउनुका साथै दाँत सफा राख्न र चपाउन निकै सजिलो बनाउँछ।"
            )
        }
    },
    'scaling-and-polishing': {
        'keywords': ['scaling', 'cleaning', 'teeth cleaning', 'polishing', 'tartar', 'plaque', 'दाँत सफा', 'स्केलिङ'],
        'en': {
            'title': 'Scaling & Polishing (Professional Deep Clean)',
            'definition': (
                "**Scaling & Polishing** is a preventive dental procedure that thoroughly cleans above and below the gumline to remove bacterial plaque and hard mineralized tartar (calculus) that regular toothbrushing cannot eliminate."
            ),
            'how_it_works': (
                "**The Procedure:**\n"
                "1. **Ultrasonic Scaling:** An ultrasonic scaler uses microscopic vibrations and cooling water mist to safely break up hardened tartar.\n"
                "2. **Polishing:** A specialized prophy paste gently buffs away surface tea/coffee stains, leaving tooth surfaces silky smooth.\n"
                "• **Does it damage enamel?** No! The vibrations do not harm enamel or loosen teeth; they remove disease-causing tartar deposits."
            ),
            'benefits': (
                "💡 **Recommended Frequency:** Every 6 months to stop bleeding gums, prevent gingivitis, and maintain fresh breath."
            )
        },
        'ne': {
            'title': 'दाँत सफा गर्ने (Scaling & Polishing)',
            'definition': (
                "**स्केलिङ (Scaling)** भनेको ब्रसले नजाने दाँतमा जमेको पहेँलो फोहोर, ढुङ्गा (Tartar/Calculus) र ब्याक्टेरियालाई अत्याधुनिक अल्ट्रासोनिक मेसिनद्वारा सफा गर्ने विधि हो।"
            ),
            'how_it_works': (
                "• अल्ट्रासोनिक भाइब्रेसन र पानीको फोहराले दाँतको इनामेललाई कुनै क्षति नपुर्याई केवल फोहोर मात्र हटाउँछ।\n"
                "• त्यसपछि दाँतलाई पोलिसिङ गरी चम्किलो र चिल्लो बनाइन्छ।"
            ),
            'benefits': (
                "💡 **के स्केलिङले दाँत कमजोर हुन्छ?**\n"
                "हुँदैन! स्केलिङले गिजा स्वस्थ राख्छ, रगत आउन रोक्छ र सास गन्हाउने समस्या पूर्ण रूपमा हटाउँछ। ६/६ महिनामा स्केलिङ गराउनु उत्तम हुन्छ।"
            )
        }
    },
    'crowns-and-bridges': {
        'keywords': ['crown', 'crowns', 'bridge', 'bridges', 'cap', 'tooth cap', 'क्याप', 'ब्रिज', 'दाँतको क्याप'],
        'en': {
            'title': 'Dental Crowns & Bridges',
            'definition': (
                "A **Dental Crown (Cap)** is a custom-made prosthetic shell that completely covers a damaged, cracked, or root-canal-treated tooth to restore its structural integrity and look. "
                "A **Dental Bridge** replaces one or more missing teeth by anchoring artificial teeth between two crowned supporting teeth."
            ),
            'how_it_works': (
                "**Materials Available:** High-translucency Zirconia, E-Max aesthetic ceramic, and Porcelain-Fused-to-Metal (PFM). Customized to blend invisibly with your smile."
            ),
            'benefits': (
                "💡 Protects fragile teeth from breaking and restores 100% natural chewing force."
            )
        },
        'ne': {
            'title': 'दाँतको क्याप तथा ब्रिज (Crowns & Bridges)',
            'definition': (
                "**दाँतको क्याप (Crown)** भनेको कमजोर, भाँचिएको वा रूट क्यानल गरिएको दाँतलाई फुट्नबाट जोगाउन माथिबाट लगाइने बलियो खोल हो। **ब्रिज (Bridge)** ले झरेको दाँतको ठाउँमा दायाँबायाँका दाँतको सहारा लिएर नयाँ दाँत राख्छ।"
            ),
            'how_it_works': (
                "• जिरकोनिया (Zirconia) र ई-म्याक्स (E-Max) जस्ता बलिया र प्राकृतिक देखिने सामग्री प्रयोग गरिन्छ।"
            ),
            'benefits': (
                "💡 दाँतलाई लामो समयसम्म बलियो राख्छ र सहज रूपमा कडा खाना चपाउन मद्दत गर्छ।"
            )
        }
    },
    'teeth-whitening': {
        'keywords': ['whitening', 'teeth whitening', 'bleaching', 'white teeth', 'ह्वाइटनिङ', 'दाँत सेतो'],
        'en': {
            'title': 'Professional Cosmetic Teeth Whitening',
            'definition': (
                "**Teeth Whitening** is a safe, non-invasive cosmetic dental procedure that removes stubborn deep stains and discoloration from tooth enamel caused by tea, coffee, smoking, tobacco, or natural aging."
            ),
            'how_it_works': (
                "• Professional dental-grade whitening gel is applied to teeth and activated with a specialized LED laser light for 60 to 90 minutes.\n"
                "• Brightens your teeth by 6 to 8 shades in a single in-clinic appointment."
            ),
            'benefits': (
                "💡 Instantly creates a bright, radiant, camera-ready smile without altering tooth structure."
            )
        },
        'ne': {
            'title': 'दाँत चम्काउने (Teeth Whitening)',
            'definition': (
                "**दाँत ह्वाइटनिङ** भनेको चिया, कफी, धुम्रपान वा उमेरका कारण पहेंलो वा कालो भएको दाँतलाई ६ देखि ८ गुणा बढी सेतो र चम्किलो बनाउने सुरक्षित कस्मेटिक विधि हो।"
            ),
            'how_it_works': (
                "• क्लिनिकमा मात्र १ घण्टामै विशेष जेल र नीलो प्रकाश (LED) को मद्दतले दाँत चम्काइन्छ।"
            ),
            'benefits': (
                "💡 दाँतको सतहलाई कुनै हानि नगरी तत्काल आकर्षक र सेतो मुस्कान प्रदान गर्दछ।"
            )
        }
    },
    'tooth-extraction': {
        'keywords': ['extraction', 'tooth extraction', 'pull tooth', 'remove tooth', 'wisdom tooth', 'दाँत निकाल्ने', 'दाँत उखेल्ने'],
        'en': {
            'title': 'Painless Tooth Extraction & Wisdom Tooth Removal',
            'definition': (
                "**Tooth Extraction** is the gentle removal of a tooth from its dental alveolus (socket) in the bone. It is performed only when a tooth is damaged beyond repair or when wisdom teeth are impacted and cause severe pain or crowding."
            ),
            'how_it_works': (
                "• Performed under profound local anesthesia so you feel only mild pressure, zero sharp pain.\n"
                "• Recovery takes 2 to 3 days with straightforward aftercare guidelines."
            ),
            'benefits': (
                "💡 Prevents painful infections from spreading to neighboring teeth and jawbone."
            )
        },
        'ne': {
            'title': 'दुखाइरहित दाँत निकाल्ने सेवा (Tooth Extraction)',
            'definition': (
                "**दाँत निकाल्ने (Extraction)** भनेको जोगाउनै नसकिने गरी बिग्रिएको वा समस्या दिएको बुद्धि बंगारालाई दुखाइरहित तरिकाले हटाउने विधि हो।"
            ),
            'how_it_works': (
                "• आधुनिक लठ्याउने औषधिको प्रयोगले गर्दा दाँत निकाल्दा कुनै दुखाइ महसुस हुँदैन।"
            ),
            'benefits': (
                "💡 अन्य राम्रा दाँत र गिजामा संक्रमण फैलिनबाट जोगाउँछ।"
            )
        }
    }
}


def find_educational_concept(query: str) -> Optional[Dict[str, Any]]:
    """Searches the educational dental encyclopedia for matching concept."""
    q_lower = query.lower()
    for slug, data in DENTAL_EDUCATIONAL_ENCYCLOPEDIA.items():
        for kw in data['keywords']:
            if kw in q_lower:
                return {'slug': slug, **data}
    return None
