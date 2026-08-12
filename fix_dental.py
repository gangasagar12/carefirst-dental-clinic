import re

def fix_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Standardize section headings
    content = re.sub(r'text-2xl md:text-3xl font-bold text-navy', r'text-[24px] md:text-[28px] font-bold text-[#102A43]', content)
    content = re.sub(r'text-3xl md:text-4xl font-bold text-navy', r'text-[24px] md:text-[28px] font-bold text-[#102A43]', content)

    # 2. Standardize heading/text sizes inside cards and lists
    content = content.replace('text-xl', 'text-[16px]')
    content = content.replace('text-lg', 'text-[13px]')
    content = content.replace('text-sm', 'text-[13px]')
    
    # 3. Standardize colors
    content = content.replace('text-navy', 'text-[#102A43]')
    content = content.replace('text-primary', 'text-[#4285F4]')
    content = content.replace('text-gray-600', 'text-gray-500')
    content = content.replace('border-primary', 'border-[#4285F4]')
    content = content.replace('bg-navy', 'bg-[#102A43]')
    content = content.replace('bg-primary', 'bg-[#4285F4]')

    # 4. Fix Section 8 (Benefits) to use cards
    old_sec8 = """<div class="grid grid-cols-1 md:grid-cols-2 gap-10 lg:gap-16 max-w-4xl mx-auto">
            <div class="border-l-4 border-[#4285F4] pl-6">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Prevents Further Decay</h3>
                <p class="text-gray-500 text-[13px] m-0">Effectively seals the cavity and protects the vulnerable inner layers of the tooth from harmful bacteria.</p>
            </div>
            <div class="border-l-4 border-[#4285F4] pl-6">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Relieves Sensitivity</h3>
                <p class="text-gray-500 text-[13px] m-0">Significantly reduces or eliminates sharp pain and discomfort experienced during eating and drinking.</p>
            </div>
            <div class="border-l-4 border-[#4285F4] pl-6">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Preserves Natural Teeth</h3>
                <p class="text-gray-500 text-[13px] m-0">Stops decay in its tracks, helping you avoid more extensive treatments like root canals or extractions later.</p>
            </div>
            <div class="border-l-4 border-[#4285F4] pl-6">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Improves Appearance</h3>
                <p class="text-gray-500 text-[13px] m-0">Modern tooth-colored composite fillings blend completely naturally with the exact shade of your smile.</p>
            </div>
        </div>"""
    new_sec8 = """<div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div class="bg-white p-6 rounded-[20px] shadow-sm border-l-4 border-[#4285F4]">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Prevents Further Decay</h3>
                <p class="text-gray-500 text-[13px] m-0">Effectively seals the cavity and protects the vulnerable inner layers of the tooth from harmful bacteria.</p>
            </div>
            <div class="bg-white p-6 rounded-[20px] shadow-sm border-l-4 border-[#4285F4]">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Relieves Sensitivity</h3>
                <p class="text-gray-500 text-[13px] m-0">Significantly reduces or eliminates sharp pain and discomfort experienced during eating and drinking.</p>
            </div>
            <div class="bg-white p-6 rounded-[20px] shadow-sm border-l-4 border-[#4285F4]">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Preserves Natural Teeth</h3>
                <p class="text-gray-500 text-[13px] m-0">Stops decay in its tracks, helping you avoid more extensive treatments like root canals or extractions later.</p>
            </div>
            <div class="bg-white p-6 rounded-[20px] shadow-sm border-l-4 border-[#4285F4]">
                <h3 class="text-[16px] font-bold text-[#102A43] mb-2">Improves Appearance</h3>
                <p class="text-gray-500 text-[13px] m-0">Modern tooth-colored composite fillings blend completely naturally with the exact shade of your smile.</p>
            </div>
        </div>"""
    content = content.replace(old_sec8, new_sec8)
    
    # 5. Fix Section 9 (Step by step circle size from w-16 to w-12 to match 16px/13px layout better)
    content = content.replace('w-16 h-16 rounded-full bg-[#102A43] text-white flex items-center justify-center text-2xl', 'w-12 h-12 rounded-full bg-[#102A43] text-white flex items-center justify-center text-[16px]')
    content = content.replace('w-16 h-16 rounded-full bg-[#4285F4] text-white flex items-center justify-center text-2xl', 'w-12 h-12 rounded-full bg-[#4285F4] text-white flex items-center justify-center text-[16px]')

    # 6. Replace Section 16 CTA entirely
    cta_start = content.find('<!-- 16. Final Conversion Section -->')
    if cta_start != -1:
        new_cta = """<!-- 16. Final Conversion Section -->
<section class="py-16 lg:py-24 bg-gray-50">
    <div class="container mx-auto px-4 max-w-[800px]">
        <div class="bg-white rounded-[20px] p-10 shadow-lg border-t-4 border-[#4285F4] text-center">
            <h2 class="text-[20px] md:text-[24px] font-bold text-[#102A43] mb-4">
                Restore Your Smile with Confidence
            </h2>
            <p class="text-[13px] text-gray-500 max-w-2xl mx-auto mb-8 leading-relaxed">
                Experiencing tooth sensitivity, a cavity, or a chipped tooth? Book a consultation at CareFirst Dental Clinic for a comfortable and natural-looking restoration.
            </p>
            <div class="flex flex-col sm:flex-row justify-center items-center gap-4">
                <a href="{% url 'appointment' %}" class="w-full sm:w-auto bg-[#4285F4] text-white font-bold text-[13px] py-3 px-8 rounded-full hover:bg-blue-600 transition-all duration-300 no-underline shadow-sm">
                    Book Appointment
                </a>
                <a href="tel:+9779807464136" class="w-full sm:w-auto bg-white border border-gray-200 text-[#102A43] font-bold text-[13px] py-3 px-8 rounded-full hover:bg-gray-50 transition-all duration-300 no-underline shadow-sm">
                    Call +977 980-7464136
                </a>
            </div>
        </div>
    </div>
</section>

{% endblock %}"""
        content = content[:cta_start] + new_cta

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_html(r'c:\Users\Chandra kant joshi\Desktop\carefirst\templates\treatments\dental_filling.html')
