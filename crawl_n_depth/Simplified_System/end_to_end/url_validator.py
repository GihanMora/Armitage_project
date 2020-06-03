
a = 'asas asasasa'
print(a.split(','))


b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt','r')
black_list = b_list_file.read().splitlines()

urls_f = open('urls.txt','r')
received_links = urls_f.read().splitlines()
# print(received_links)
# print(received_links)
received_domains = [i.split("/")[2] for i in received_links]
filtered_sr = []

# print('rd', received_domains)
print(len(received_domains))
c=0
ggs = []
probs = []
for i, each in enumerate(received_links):
    if (('.gov.' in each) or ('.govt.' in each) or ('.edu.' in each) ):  # filter non wanted websites
        # print(each)
        ggs.append(each)
        continue
    if(('.com/' in each) or ('.education/' in each) or ('.io/' in each) or ('.com.au/' in each) or ('.net/' in each) or ('.org/' in each) or ('.co.nz/' in each) or ('.nz/' in each) or ('.au/' in each) or ('.biz/' in each)):
            # print(each)
            c+=1
    else:
        probs.append(each)
print(c)
print(ggs)
print(probs)



# ['https://aie.edu.au/', 'https://www.dss.gov.au/', 'https://agedcare.royalcommission.gov.au/', 'https://www.gets.govt.nz/', 'https://www.gets.govt.nz/', 'http://www.education.govt.nz/', 'http://www.education.govt.nz/', 'https://www.newzealandnow.govt.nz/', 'https://www.rmit.edu.au/', 'https://www.griffith.edu.au/', 'https://study.unisa.edu.au/', 'https://www.torrens.edu.au/', 'https://www.vu.edu.au/', 'https://www.mpi.govt.nz/', 'https://kts.edu.au/', 'http://angad.vic.edu.au/', 'https://www.mcie.edu.au/', 'https://www.upskilled.edu.au/', 'https://www.scopeiteducation.edu.au/', 'https://www.uts.edu.au/staff/jason.prior', 'https://www.eworks.edu.au/about/', 'https://www.studyinnewzealand.govt.nz/', 'https://study.csu.edu.au/', 'https://www.mbie.govt.nz/', 'http://www.education.govt.nz/', 'http://www.education.govt.nz/', 'http://www.education.govt.nz/', 'https://research.acer.edu.au/', 'https://www.trb.wa.gov.au/', 'https://www.careers.govt.nz/', 'https://www.audit.nsw.gov.au/', 'https://www.parliament.wa.gov.au/', 'https://ro.uow.edu.au/', 'https://audit.wa.gov.au/', 'https://www2.health.vic.gov.au/', 'https://tasa.edu.au/', 'https://www.matrix.edu.au/', 'https://www.cbdcollege.edu.au/', 'https://dc.edu.au/', 'https://www.uit.edu.au/', 'https://www.mft.edu.au/', 'https://www.sitcm.edu.au/', 'https://www.gca.edu.au/', 'https://www.macleay.edu.au/', 'https://www.raffles.edu.au/', 'https://www.achw.edu.au/', 'https://www.mit.edu.au/', 'http://www.sage.edu.au/', 'https://www.icms.edu.au/', 'https://kent.edu.au/kent3/', 'https://www.lcimelbourne.edu.au/', 'https://marcusoldham.vic.edu.au/', 'https://www.ptacademy.edu.au/', 'https://www.aib.edu.au/about-us/', 'https://www.apc.edu.au/about-us/', 'https://www.psc.edu.au/', 'https://www.skills.vic.gov.au/victorianskillsgateway/Mobile/Pages/providersearchdescription.aspx?type=provider&searchid=491', 'https://ozford.edu.au/', 'https://jti.edu.au/', 'https://whitehouse-design.edu.au/', 'https://www.eca.edu.au/', 'https://whitehouse-design.edu.au/', 'https://www.eca.edu.au/', 'https://www.vit.edu.au/', 'https://www.jmcacademy.edu.au/', 'https://www.acknowledgeeducation.edu.au/', 'https://www.ducere.edu.au/', 'http://www.intercontinental.edu.au/', 'https://www.tibc.nsw.edu.au/about-us/about.html', 'https://www.iibit.edu.au/', 'https://soar.edu.au/', 'https://williams.edu.au/', 'https://seda.edu.au/', 'https://aisi.edu.au/', 'https://www.ash.edu.au/', 'https://www.demiinternational.edu.au/', 'https://ergt.edu.au/about-us/', 'http://www.schoolofbeauty.nsw.edu.au/', 'https://www.aot.edu.au/about-aot/', 'https://acbc.nsw.edu.au/about-acbc/', 'https://strategix.edu.au/strategix-our-story/', 'https://vfalearning.vic.edu.au/', 'https://www.nicheeducation.edu.au/about/', 'https://www.ausacademy.edu.au/', 'https://www.ctiaustralia.edu.au/content/about-us', 'https://itfutures.edu.au/about/', 'https://kirana.edu.au/about-us/', 'https://www.lonsdaleinstitute.edu.au/about/', 'https://linx.edu.au/about-us/', 'https://www.mayfield.edu.au/about-us/', 'https://selmar.edu.au/about-us/', 'https://www.monarch.edu.au/about/','https://courselink.uoguelph.ca/', 'https://digiskool.co.ke/', 'https://www.centennialcollege.ca/', 'https://www.agenciaversato.com.br/', 'https://www.nyfa.edu/', 'https://www.northumbria.ac.uk/', 'http://solonely.fr/', 'https://www.teletracnavman.co.uk/', 'https://www.wisenet.co/about-us', 'https://mathspace.co/', 'https://resolve.consulting/', 'https://risingsunoverport.co.za/47278/cellphone-app-curb-child-abuse/', 'https://aro.digital/', 'https://www.infocubic.co.jp/en/', 'https://www.jica.go.jp/', 'https://www.hill-rom.es/', 'https://www.trueblue.financial/', 'https://www.secureco.co/', 'http://www.dadm.xyz/', 'https://www.titanium.solutions/', 'https://dresden.vision/', 'https://www.appliedcare.co.uk/site-services/contacts.aspx', 'https://iomni.ai/', 'https://rocketreach.co/confurmo-profile_b55809dcf62dbbb7', 'http://www.dingosoft.co/', 'https://mobecom.co/', 'https://www.gbw.solutions/', 'https://rocketreach.co/peakbound-holdings-pty-profile_b5e0104af42e6f7a', 'https://www.homburger.ch/', 'https://algenett.no/rapporterogartikler', 'https://www.cambridgecollege.edu/', 'https://www.spconsult.uz/en/list/info/type/org/id/6/', 'https://www.els.edu/', 'https://echogroup.co/', 'https://xdi.systems/', 'https://vetsoncall.pet/', 'https://rocketreach.co/chikale-resources-profile_b5a36fb5f9b770fa', 'https://autumn.care/', 'https://www.safer.me/', 'http://www.unlockd.co.za/site/index', 'https://schooltv.me/', 'https://cyberresearch.co/category/security-information/', 'http://www.cybercity.com.jo/']
