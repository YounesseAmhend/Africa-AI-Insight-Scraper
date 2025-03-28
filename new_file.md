# This is a new Markdown file

You will be provided with HTML code representing a webpage. Your task is to extract specific information from this HTML using CSS selectors compatible with BeautifulSoup. 

Generate a Python dictionary conforming to the following structure:

```python
{
    "title": "CSS selector for the title of each news article",
    "link": "CSS selector for the link to each news article",
    "load_more_button": "CSS selector for the 'load more' button (if present, otherwise None)",
    "next_button": "CSS selector for the 'next' page button (if present, otherwise None)"
}
```

### Instructions

1. **Title**: Identify the CSS selector for the HTML elements containing the title of each news article.
2. **Link**: Identify the CSS selector for the HTML elements containing the links to each news article.
3. **Load More Button**: Identify the CSS selector for the "load more" button if the webpage uses infinite scrolling or a "load more" feature. If not present, set this to `None`.
4. **Next Button**: Identify the CSS selector for the "next" page button if the webpage uses pagination. If not present, set this to `None`.

### Output Format

Ensure the output is a Python dictionary in the exact format shown above, with no additional comments or explanations.

### Example Output

```python
{
    "title": "ul.news-list li h4",
    "link": "ul.news-list li a",
    "load_more_button": None,
    "next_button": "ul.pagination li.next a"
}
```
### HTML Code for Analysis

```html
<nav id="menu" class="zp-block-menublock-menu mm-menu mm-pageshadow mm-theme-dark mm-offcanvas"><form class="search-form zp-validate-standard-form" action="https://www.up.ac.za/search" method="get" novalidate="novalidate">
                    <div class="typeahead__container">
                      <div class="typeahead__field">
                        <span class="typeahead__query">
                          <input class="js-typeahead" name="term" type="search" autocomplete="off" placeholder="Search for...">
                        </span>
                        <span class="typeahead__button">
                          <button type="submit" aria-label="Search">
                            <i class="fa fa-search"></i>
                          </button>
                        </span>
                      </div>
                    </div>
                  </form><button id="close" class="menu-btn" aria-label="Close"><i class="fa fa-times-circle"></i></button><div class="mm-panel mm-hasnavbar mm-opened mm-current" id="mm-1"><div class="mm-navbar"><a class="mm-title">Menu</a></div><ul class="mm-listview mm-first mm-last">
                                        <li>
                      <a class="mm-next" href="#mm-2" data-target="#mm-2"></a><a href="https://www.up.ac.za/article/2749257/about-us">About UP</a>
                                          </li>
                                        <li>
                      <a class="mm-next" href="#mm-3" data-target="#mm-3"></a><a href="https://www.up.ac.za/article/2749245/study">Study</a>
                                          </li>
                                        <li>
                      <a class="mm-next" href="#mm-4" data-target="#mm-4"></a><a href="https://www.up.ac.za/article/2749285/research">Research</a>
                                          </li>
                                        <li>
                      <a class="mm-next" href="#mm-5" data-target="#mm-5"></a><a href="https://www.up.ac.za/article/2749279/campus-life">Campus Life</a>
                                          </li>
                                        <li>
                      <a class="mm-next" href="#mm-6" data-target="#mm-6"></a><a href="https://www.up.ac.za/advancement-fundraising" target="_blank">Giving to UP</a>
                                          </li>
                                        <li>
                      <a href="https://www.up.ac.za/article/3208511/contact-us">Contact Us</a>
                                          </li>
                                        <li>
                      <a href="/students">Students</a>
                                          </li>
                                        <li>
                      <a href="/parents">Parents and Guardians</a>
                                          </li>
                                        <li>
                      <a href="/alumni">Alumni</a>
                                          </li>
                                        <li>
                      <a href="/visitors">Visitors</a>
                                          </li>
                                        <li>
                      <a href="/up-media">Media</a>
                                          </li>
                                        <li>
                      <a href="http://www.library.up.ac.za/" target="_blank">Library</a>
                                          </li>
                                                        </ul></div><div class="mm-panel mm-hasnavbar mm-hidden" id="mm-2"><div class="mm-navbar"><a class="mm-btn mm-prev" href="#mm-1" data-target="#mm-1"></a><a class="mm-title" href="#mm-1">About UP</a></div><ul class="mm-listview mm-first mm-last">
                                                                              <li><a href="https://www.up.ac.za/article/2749381/our-story">Our Story</a></li>
                                                                              <li><a href="/teaching-and-learning" target="_blank">Teaching and Learning</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749291/management-governance">Management and Governance </a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2754069/up-policies-and-other-important-documents">UP Policies</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749387/world-rankings">World Rankings</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749429/internationalization-and-global-engagements">Internationalization and Global engagements</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749393/faculties">Faculties</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749435/campuses-maps-directions-">Campuses, Maps &amp; Directions</a></li>
                                                                              <li><a href="/institutes-and-centres" target="_blank">Institutes, Centers and Units</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749712/enterprises">Enterprises</a></li>
                                                                              <li><a href="/support-services" target="_blank">Professional Services</a></li>
                                                                              <li><a href="https://www.up.ac.za/usr" target="_blank">Social Responsibility</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749769/news-and-events">News and Events</a></li>
                                                                              <li><a href="/department-of-institutional-advancement/article/1967841/the-university-of-pretoria-publications" target="_blank">Publications</a></li>
                                                                              <li><a href="https://www.up.ac.za/human-resources-department/article/257103/careersup">Career Opportunities</a></li>
                                                                              <li><a href="/tender/">Tenders</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2829394/the-up-way">THE UP WAY</a></li>
                                                                              <li><a href="https://digitaltransformation.up.ac.za/" target="_blank">Digital Transformation</a></li>
                                                                              <li><a href="https://issuu.com/universityofpretoria/docs/up_sdp_2030_epub_59mb?fr=sMTU3Njc2NzQ3NTY" target="_blank">Spatial Development Plan 2030</a></li>
                                                  </ul></div><div class="mm-panel mm-hasnavbar mm-hidden" id="mm-3"><div class="mm-navbar"><a class="mm-btn mm-prev" href="#mm-1" data-target="#mm-1"></a><a class="mm-title" href="#mm-1">Study</a></div><ul class="mm-listview mm-first mm-last">
                                                                              <li><a href="/programmes" target="_blank">What to Study</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749188/what-to-expect">What to Expect</a></li>
                                                                              <li><a href="/online-application" target="_blank">Apply</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749200/fees-and-funding">Fees and Funding</a></li>
                                                                              <li><a href="http://www.library.up.ac.za/" target="_blank">Libraries</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749212/student-success">Student Success</a></li>
                                                                              <li><a href="/student-affairs" target="_blank">Student Affairs</a></li>
                                                                              <li><a href="/yearbooks/home">Yearbooks</a></li>
                                                                              <li><a href="/disability-unit">Disability Unit</a></li>
                                                                              <li><a href="http://www.enterprises.up.ac.za/">Short Courses</a></li>
                                                                              <li><a href="https://www.up.ac.za/international-cooperation-division/article/3005898/international-students" target="_blank">International Students</a></li>
                                                                              <li><a href="https://www.up.ac.za/graduate-support-hub">Postgraduate</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749239/school-learners">School Learners</a></li>
                                                                              <li><a href="https://linus.up.ac.za/calendars/">UP Calendar</a></li>
                                                                              <li><a href="https://www.gibs.co.za/">Gordon Institute Business of Science - GIBS</a></li>
                                                                              <li><a href="/uponline">UPOnline</a></li>
                                                  </ul></div><div class="mm-panel mm-hasnavbar mm-hidden" id="mm-4"><div class="mm-navbar"><a class="mm-btn mm-prev" href="#mm-1" data-target="#mm-1"></a><a class="mm-title" href="#mm-1">Research</a></div><ul class="mm-listview mm-first mm-last">
                                                                              <li><a href="https://www.up.ac.za/article/2749375/research-overview">Overview</a></li>
                                                                              <li><a href="/leaders-in-research" target="_blank">UP Leaders in Research</a></li>
                                                                              <li><a href="/research-reports-and-news" target="_blank">Research Report and News</a></li>
                                                                              <li><a href="/research-focus-areas" target="_blank">Focus Areas</a></li>
                                                                              <li><a href="/research-support" target="_blank">Research Support</a></li>
                                                                              <li><a href="/research-and-innovation" target="_blank">Research Innovation</a></li>
                                                                              <li><a href="/postgraduate-study-and-research" target="_blank">Postgraduate Study and Research</a></li>
                                                                              <li><a href="/international-cooperation-division" target="_blank">International Cooperation</a></li>
                                                                              <li><a href="/postdoctoral-research" target="_blank">Postdoctoral Research</a></li>
                                                                              <li><a href="https://library.up.ac.za/research" target="_blank">Library Research Services</a></li>
                                                  </ul></div><div class="mm-panel mm-hasnavbar mm-hidden" id="mm-5"><div class="mm-navbar"><a class="mm-btn mm-prev" href="#mm-1" data-target="#mm-1"></a><a class="mm-title" href="#mm-1">Campus Life</a></div><ul class="mm-listview mm-first mm-last">
                                                                              <li><a href="/article/2749423/accommodation-and-places-to-eat" target="_blank">Accommodation &amp; Places to Eat</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749571/arts-culture-and-museums">Arts, Culture and Museums</a></li>
                                                                              <li><a href="/student-affairs/article/3284348/student-health-services-shs" target="_blank">Student Health Services</a></li>
                                                                              <li><a href="/tukssport">TuksSport</a></li>
                                                                              <li><a href="/department-of-security-services/article/23390/safety-on-campus" target="_blank">Safety on Campus</a></li>
                                                                              <li><a href="/article/2749435/campuses-maps-directions">Campuses, Maps &amp; Directions</a></li>
                                                                              <li><a href="/student-affairs/article/3284327/student-governance-and-leadership-sgal" target="_blank">Student Governance and Leadership</a></li>
                                                                              <li><a href="/student-affairs/article/3284334/student-development-and-disability-unit-sddu " target="_blank">Student Development and Disability unit</a></li>
                                                                              <li><a href="/disability-unit">Disability Unit</a></li>
                                                                              <li><a href="/up-wireless-network/article/277134/wifi-coverage-maps-campus-view">Wi-Fi Access</a></li>
                                                                              <li><a href="https://virtualcampus.up.ac.za/">Virtual Campus</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749949/things-to-do">Things to Do</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749763/transport-and-getting-to-campus">Transport and getting to campus</a></li>
                                                                              <li><a href="/student-affairs/article/3284341/student-counselling-unit-scu">Student Counselling</a></li>
                                                                              <li><a href="/student-affairs/article/3284355/flyup" target="_blank">FLY@UP</a></li>
                                                  </ul></div><div class="mm-panel mm-hasnavbar mm-hidden" id="mm-6"><div class="mm-navbar"><a class="mm-btn mm-prev" href="#mm-1" data-target="#mm-1"></a><a class="mm-title" href="#mm-1">Giving to UP</a></div><ul class="mm-listview mm-first mm-last">
                                                                              <li><a href="/advancement-fundraising/article/257493/ways-to-give">Ways to Give</a></li>
                                                                              <li><a href="https://www.up.ac.za/advancement-fundraising/article/3165178/up-giving-day-campaign">Giving Day Campaign</a></li>
                                                                              <li><a href="/advancement-fundraising/article/2748094/benefits-of-giving">Benefits of Giving</a></li>
                                                                              <li><a href="https://www.up.ac.za/article/2749417/social-responsibility">Social Responsiveness</a></li>
                                                                              <li><a href="/advancement-fundraising/article/2748057/fundraising-priorities">Fundraising Priorities</a></li>
                                                                              <li><a href="/advancement-fundraising/article/2730253/contact-us">Contact Us</a></li>
                                                  </ul></div></nav>
                    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W56M5WL" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <div id="mm-0" class="mm-page mm-slideout"><div class="site-blur-container" style="display: block;"></div><div id="cookie-preferences-container" class="cookie-preferences-container" data-url="https://www.up.ac.za/cookie-preferences/controls/" style="display: block;">
<div id="cookie-preferences" class="cookie-preferences">
    <div class="container simple d-flex align-items-center">
        <div class="row w-100">
            <div class="col-12 col-lg-8 text-center text-lg-left">
                <h3>Cookies</h3>
                <p class="my-2">We collect information through cookies to enable our website to function optimally, read more&nbsp;<a href="https://www.up.ac.za/web-office/article/2884659/website-privacy-notice">here</a>.</p>
            </div>
            <div class="col-12 col-lg-4 text-center text-lg-right">
                <div class="col-12 mb-lg-2">
                    <button class="btn m-1 w-100 rounded btn-outline" id="cookie-preferences-manage">Customize cookie preferences</button>
                </div>
                <div class="col-12">
                    <button class="btn text-white m-1 w-100 rounded" id="cookie-preferences-accept-all">Accept all</button>
                </div>
            </div>
        </div>
    </div>
    <div class="container granular">
        <div class="row">
            <div class="col-md-12">
                <h3>Cookie information <i class="fa fa-exclamation-circle"></i></h3>
                                <p>We collect information through cookies to enable our website to function optimally. We also set statistic and preference cookies to help us improve our website.</p>
                                <p>When you use this preference tool it will set a cookie on your device to remember your preferences.</p>
                                <p>If you want more information about the cookies we use, read our&nbsp;<a href="https://www.up.ac.za/web-office/article/2884659/website-privacy-notice">privacy&nbsp;notice</a>.</p>
                            </div>
            <div class="col-md-12">
                <h3>Cookie preferences <i class="fa fa-cog"></i></h3>
                <form id="cookiePreferencesForm" name="cookiePreferencesForm" action="https://www.up.ac.za/cookie-preferences/controls/" method="post" novalidate="novalidate" class="zp-validate-standard-form">
                    <input type="hidden" name="save" value="yes">
                                        <div class="row">
                        <div class="col-9">
                            <p class=""><b>Essential cookies</b> are necessary for our website to function. <a href="https://www.up.ac.za/web-office/article/2895076/essential-cookies" class="link">Read&nbsp;more&nbsp;<i class="fa fa-angle-double-right"></i></a></p>
                        </div>
                        <div class="col-3 pb-2 pb-md-0 text-right">
                                                        <div class="toggle btn btn-success btn-sm disabled" data-toggle="toggle" role="button" disabled="disabled" style="width: 0px; height: 0px;"><input class="" disabled="" type="checkbox" checked="checked" data-toggle="toggle" data-size="sm" data-onstyle="success"><div class="toggle-group"><label for="" class="btn btn-success btn-sm toggle-on">On</label><label for="" class="btn btn-light btn-sm toggle-off">Off</label><span class="toggle-handle btn btn-light btn-sm"></span></div></div>
                                                    </div>
                    </div>
                                        <div class="row">
                        <div class="col-9">
                            <p class=""><b>Statistic cookies</b> are used to collect statistical information about website usage. <a href="https://www.up.ac.za/web-office/article/2895064/statistic-cookies" class="link">Read&nbsp;more&nbsp;<i class="fa fa-angle-double-right"></i></a></p>
                        </div>
                        <div class="col-3 pb-2 pb-md-0 text-right">
                                                        <div class="toggle btn btn-success btn-sm" data-toggle="toggle" role="button" style="width: 0px; height: 0px;"><input class="" type="checkbox" id="cookiePreferences_statistic" name="cookiePreferences_statistic" value="1" data-toggle="toggle" data-size="sm" data-onstyle="success" data-offstyle="danger" checked="checked"><div class="toggle-group"><label for="cookiePreferences_statistic" class="btn btn-success btn-sm toggle-on">On</label><label for="cookiePreferences_statistic" class="btn btn-danger btn-sm toggle-off">Off</label><span class="toggle-handle btn btn-light btn-sm"></span></div></div>
                                                    </div>
                    </div>
                                        <div class="row">
                        <div class="col-9">
                            <p class=""><b>Preference cookies</b> are used to store your preferences. <a href="https://www.up.ac.za/web-office/article/2895082/preference-cookies" class="link">Read&nbsp;more&nbsp;<i class="fa fa-angle-double-right"></i></a></p>
                        </div>
                        <div class="col-3 pb-2 pb-md-0 text-right">
                                                        <div class="toggle btn btn-success btn-sm" data-toggle="toggle" role="button" style="width: 0px; height: 0px;"><input class="" type="checkbox" id="cookiePreferences_preferences" name="cookiePreferences_preferences" value="1" data-toggle="toggle" data-size="sm" data-onstyle="success" data-offstyle="danger" checked="checked"><div class="toggle-group"><label for="cookiePreferences_preferences" class="btn btn-success btn-sm toggle-on">On</label><label for="cookiePreferences_preferences" class="btn btn-danger btn-sm toggle-off">Off</label><span class="toggle-handle btn btn-light btn-sm"></span></div></div>
                                                    </div>
                    </div>
                                        <div class="row">
                        <div class="col-9">
                            <p class=""><b>Marketing cookies</b> are used for advertising purposes. <a href="https://www.up.ac.za/web-office/article/2895070/marketing-cookies" class="link">Read&nbsp;more&nbsp;<i class="fa fa-angle-double-right"></i></a></p>
                        </div>
                        <div class="col-3 pb-2 pb-md-0 text-right">
                                                        <div class="toggle btn btn-danger off btn-sm" data-toggle="toggle" role="button" style="width: 0px; height: 0px;"><input class="" type="checkbox" id="cookiePreferences_marketing" name="cookiePreferences_marketing" value="1" data-toggle="toggle" data-size="sm" data-onstyle="success" data-offstyle="danger"><div class="toggle-group"><label for="cookiePreferences_marketing" class="btn btn-success btn-sm toggle-on">On</label><label for="cookiePreferences_marketing" class="btn btn-danger btn-sm toggle-off">Off</label><span class="toggle-handle btn btn-light btn-sm"></span></div></div>
                                                    </div>
                    </div>
                                    <input type="hidden" value="0b81b533599dceca9fc82de2a821a23c53844238" name="zp_token"></form>
                <button id="cookiePreferencesSave" class="btn text-white mt-md-3 rounded">Save preferences</button>
            </div>
        </div>
    </div>
</div>
</div><div class="wrapper">
      <div class="container position-relative d-none d-sm-none d-md-none d-xl-block">
        <div class="logo">
          <a href="/"><img src="/themes/up2.0/images/vertical-logo-bg.png" class="h-logo img-fluid mx-auto" alt=""></a>
        </div>
      </div>
      <div class="top-area">
        <div class="container">
          <div class="row">
            <div class="col-12 offset-xl-2 col-xl-10">
              <div class="inner">
                <div class="left">
                  <a class="toggle d-md-block d-xl-none" href="#menu" aria-label="Menu"><i class="fa fa-navicon"></i></a> 
                                      <section id="very_top_menu" class="zp-block-menublock-very_top_menu very-top-menu-wrapper">
              <ul class="list-inline d-none d-sm-none d-md-none d-xl-block">
                    <li class=""><a class="" href="/students">Students</a></li>
                    <li class=""><a class="" href="/parents">Parents and Guardians</a></li>
                    <li class=""><a class="" href="/alumni">Alumni</a></li>
                    <li class=""><a class="" href="/visitors">Visitors</a></li>
                    <li class=""><a class="" href="/up-media">Media</a></li>
                    <li class=""><a class="" href="http://www.library.up.ac.za/" target="_blank">Library</a></li>
                            <li class="clearfix"></li>
              </ul>
</section>
                                  </div>
                <div class="right">
                  <ul class="list-inline">
                    <li><a href="https://www.up.ac.za/siteindex">A-Z Index <i class="fa fa-caret-right margin-left-15"></i></a></li>
                    <li class="d-none d-sm-none d-md-none d-xl-block">
                      <form action="https://www.up.ac.za/search" method="get" novalidate="novalidate" class="zp-validate-standard-form">
                        <div class="typeahead__container">
                          <div class="typeahead__field">
                            <span class="typeahead__query">
                              <input class="js-typeahead" name="term" type="search" autocomplete="off" placeholder="Search for...">
                            </span>
                            <span class="typeahead__button">
                              <button type="submit" aria-label="Search">
                                <i class="fa fa-search"></i>
                              </button>
                            </span>
                          </div>
                        </div>
                      </form>
                    </li>
                    <li><a class="bg-color-03" href="https://upnet.up.ac.za/portal"><i class="fa fa-key margin-right-5"></i> My UP Login</a></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="header-area">
        <div class="container">
          <div class="row">
            <div class="col-xl-2 padding-right-0-991">
              <div class="logo-block pos-rel">
                <a href="/"><img src="/themes/up2.0/images/horizontal-logo-bg.png" class="v-logo mx-auto img-fluid" width="" alt=""></a>
              </div>
            </div>
            <div id="site_menu_container" class="col-lg-10 d-none d-sm-none d-md-none d-xl-block padding-left-0-991">
              <nav id="site_menu" class="zp-block-menublock-site_menu navbar yamm navbar-expand-lg">
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar" aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation">
                  <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar" role="navigation">
                  <ul class="navbar-nav nav nav-fill" role="application">
                                                                                                                                                                                                                                                                                                                          <li class="nav-item dropdown yamm-fw">
                      <a href="https://www.up.ac.za/article/2749257/about-us" aria-label="About UP" role="button" aria-haspopup="true" aria-expanded="false">About UP</a>
                                              <ul class="dropdown-menu">
                        <li>
                          <div class="yamm-content">
                            <div class="row">
                              <div class="col-sm-12">
                                <div class="row">      
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/article/2749381/our-story" aria-label="Our Story">Our Story</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/teaching-and-learning" target="_blank" aria-label="Teaching and Learning">Teaching and Learning</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749291/management-governance" aria-label="Management and Governance ">Management and Governance </a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2754069/up-policies-and-other-important-documents" aria-label="UP Policies">UP Policies</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749387/world-rankings" aria-label="World Rankings">World Rankings</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="https://www.up.ac.za/article/2749429/internationalization-and-global-engagements" aria-label="Internationalization and Global engagements">Internationalization and Global engagements</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/article/2749393/faculties" aria-label="Faculties">Faculties</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749435/campuses-maps-directions-" aria-label="Campuses, Maps &amp; Directions">Campuses, Maps &amp; Directions</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/institutes-and-centres" target="_blank" aria-label="Institutes, Centers and Units">Institutes, Centers and Units</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749712/enterprises" aria-label="Enterprises">Enterprises</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/support-services" target="_blank" aria-label="Professional Services">Professional Services</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="https://www.up.ac.za/usr" target="_blank" aria-label="Social Responsibility">Social Responsibility</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/article/2749769/news-and-events" aria-label="News and Events">News and Events</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/department-of-institutional-advancement/article/1967841/the-university-of-pretoria-publications" target="_blank" aria-label="Publications">Publications</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/human-resources-department/article/257103/careersup" aria-label="Career Opportunities">Career Opportunities</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/tender/" aria-label="Tenders">Tenders</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2829394/the-up-way" aria-label="THE UP WAY">THE UP WAY</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="https://digitaltransformation.up.ac.za/" target="_blank" aria-label="Digital Transformation">Digital Transformation</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class="border-bottom-none"><a href="https://issuu.com/universityofpretoria/docs/up_sdp_2030_epub_59mb?fr=sMTU3Njc2NzQ3NTY" target="_blank" aria-label="Spatial Development Plan 2030">Spatial Development Plan 2030</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                    </div>
                              </div>
                                                          </div>
                          </div>
                        </li>
                      </ul>
                                          </li>
                                                                                                                                                                                                                                                                    <li class="nav-item dropdown yamm-fw">
                      <a href="https://www.up.ac.za/article/2749245/study" aria-label="Study" role="button" aria-haspopup="true" aria-expanded="false">Study</a>
                                              <ul class="dropdown-menu">
                        <li>
                          <div class="yamm-content">
                            <div class="row">
                              <div class="col-sm-12">
                                <div class="row">      
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/programmes" target="_blank" aria-label="What to Study">What to Study</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749188/what-to-expect" aria-label="What to Expect">What to Expect</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/online-application" target="_blank" aria-label="Apply">Apply</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749200/fees-and-funding" aria-label="Fees and Funding">Fees and Funding</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="http://www.library.up.ac.za/" target="_blank" aria-label="Libraries">Libraries</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/article/2749212/student-success" aria-label="Student Success">Student Success</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/student-affairs" target="_blank" aria-label="Student Affairs">Student Affairs</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/yearbooks/home" aria-label="Yearbooks">Yearbooks</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/disability-unit" aria-label="Disability Unit">Disability Unit</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="http://www.enterprises.up.ac.za/" aria-label="Short Courses">Short Courses</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/international-cooperation-division/article/3005898/international-students" target="_blank" aria-label="International Students">International Students</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/graduate-support-hub" aria-label="Postgraduate">Postgraduate</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749239/school-learners" aria-label="School Learners">School Learners</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://linus.up.ac.za/calendars/" aria-label="UP Calendar">UP Calendar</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="https://www.gibs.co.za/" aria-label="Gordon Institute Business of Science - GIBS">Gordon Institute Business of Science - GIBS</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class="border-bottom-none"><a href="/uponline" aria-label="UPOnline">UPOnline</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                    </div>
                              </div>
                                                          </div>
                          </div>
                        </li>
                      </ul>
                                          </li>
                                                                                                                                                                                                                                                                    <li class="nav-item dropdown yamm-fw">
                      <a href="https://www.up.ac.za/article/2749285/research" aria-label="Research" role="button" aria-haspopup="true" aria-expanded="false">Research</a>
                                              <ul class="dropdown-menu">
                        <li>
                          <div class="yamm-content">
                            <div class="row">
                              <div class="col-sm-12">
                                <div class="row">      
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://www.up.ac.za/article/2749375/research-overview" aria-label="Overview">Overview</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/leaders-in-research" target="_blank" aria-label="UP Leaders in Research">UP Leaders in Research</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/research-reports-and-news" target="_blank" aria-label="Research Report and News">Research Report and News</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/research-focus-areas" target="_blank" aria-label="Focus Areas">Focus Areas</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/research-support" target="_blank" aria-label="Research Support">Research Support</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/research-and-innovation" target="_blank" aria-label="Research Innovation">Research Innovation</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/postgraduate-study-and-research" target="_blank" aria-label="Postgraduate Study and Research">Postgraduate Study and Research</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/international-cooperation-division" target="_blank" aria-label="International Cooperation">International Cooperation</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/postdoctoral-research" target="_blank" aria-label="Postdoctoral Research">Postdoctoral Research</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class="border-bottom-none"><a href="https://library.up.ac.za/research" target="_blank" aria-label="Library Research Services">Library Research Services</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                    </div>
                              </div>
                                                          </div>
                          </div>
                        </li>
                      </ul>
                                          </li>
                                                                                                                                                                                                                                                                    <li class="nav-item dropdown yamm-fw">
                      <a href="https://www.up.ac.za/article/2749279/campus-life" aria-label="Campus Life" role="button" aria-haspopup="true" aria-expanded="false">Campus Life</a>
                                              <ul class="dropdown-menu">
                        <li>
                          <div class="yamm-content">
                            <div class="row">
                              <div class="col-sm-12">
                                <div class="row">      
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/article/2749423/accommodation-and-places-to-eat" target="_blank" aria-label="Accommodation &amp; Places to Eat">Accommodation &amp; Places to Eat</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749571/arts-culture-and-museums" aria-label="Arts, Culture and Museums">Arts, Culture and Museums</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/student-affairs/article/3284348/student-health-services-shs" target="_blank" aria-label="Student Health Services">Student Health Services</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/tukssport" aria-label="TuksSport">TuksSport</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/department-of-security-services/article/23390/safety-on-campus" target="_blank" aria-label="Safety on Campus">Safety on Campus</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/article/2749435/campuses-maps-directions" aria-label="Campuses, Maps &amp; Directions">Campuses, Maps &amp; Directions</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/student-affairs/article/3284327/student-governance-and-leadership-sgal" target="_blank" aria-label="Student Governance and Leadership">Student Governance and Leadership</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/student-affairs/article/3284334/student-development-and-disability-unit-sddu " target="_blank" aria-label="Student Development and Disability unit">Student Development and Disability unit</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/disability-unit" aria-label="Disability Unit">Disability Unit</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/up-wireless-network/article/277134/wifi-coverage-maps-campus-view" aria-label="Wi-Fi Access">Wi-Fi Access</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                                                                                                                                                                                                <ul class="col-md-4 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="https://virtualcampus.up.ac.za/" aria-label="Virtual Campus">Virtual Campus</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749949/things-to-do" aria-label="Things to Do">Things to Do</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749763/transport-and-getting-to-campus" aria-label="Transport and getting to campus">Transport and getting to campus</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/student-affairs/article/3284341/student-counselling-unit-scu" aria-label="Student Counselling">Student Counselling</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/student-affairs/article/3284355/flyup" target="_blank" aria-label="FLY@UP">FLY@UP</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                    </div>
                              </div>
                                                          </div>
                          </div>
                        </li>
                      </ul>
                                          </li>
                                                                                                                                                                                                                                                                    <li class="nav-item dropdown ">
                      <a href="https://www.up.ac.za/advancement-fundraising" target="_blank" aria-label="Giving to UP" role="button" aria-haspopup="true" aria-expanded="false">Giving to UP</a>
                                              <ul class="dropdown-menu">
                        <li>
                          <div class="yamm-content">
                            <div class="row">
                              <div class="col-sm-12">
                                <div class="row">      
                                                                                                                                                                                                                                                                                <ul class="col-md-12 list-unstyled">
                                    <li>
                                      <ul>
                                                                          <li class=""><a href="/advancement-fundraising/article/257493/ways-to-give" aria-label="Ways to Give">Ways to Give</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/advancement-fundraising/article/3165178/up-giving-day-campaign" aria-label="Giving Day Campaign">Giving Day Campaign</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/advancement-fundraising/article/2748094/benefits-of-giving" aria-label="Benefits of Giving">Benefits of Giving</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="https://www.up.ac.za/article/2749417/social-responsibility" aria-label="Social Responsiveness">Social Responsiveness</a></li>
                                                                                                                                                                                                                                                                                      <li class=""><a href="/advancement-fundraising/article/2748057/fundraising-priorities" aria-label="Fundraising Priorities">Fundraising Priorities</a></li>
                                                                                                                                                                                                                                                                                      <li class="border-bottom-none"><a href="/advancement-fundraising/article/2730253/contact-us" aria-label="Contact Us">Contact Us</a></li>
                                                                        </ul>
                                    </li>
                                  </ul>         
                                                                                                    </div>
                              </div>
                                                          </div>
                          </div>
                        </li>
                      </ul>
                                          </li>
                                                                                                                                                                                                                                                                    <li class="nav-item  ">
                      <a href="https://www.up.ac.za/article/3208511/contact-us" aria-label="Contact Us">Contact Us</a>
                                          </li>
                                                        </ul>
                </div>
</nav>
            </div>
          </div>
        </div>
      </div>
    </div><div id="zp_news_index" class="no-print zp-view zp-news-index-view">
    <section id="banner-area" class="zp-block-frontpageblock-banner-area banner-area">
      <div id="slider" class="flexslider" aria-live="off">
        <ul class="slides" aria-live="off">
                                                            <li class="slide-plain flex-active-slide" style="width: 100%; float: left; margin-right: -100%; position: relative; display: block; z-index: 2; opacity: 1;" data-thumb-alt="">
                        <a class="d-block" href="https://www.up.ac.za/news/post_3294746-a-new-chapter-for-up-as-professor-francis-petersen-takes-the-helm-as-the-14th-vice-chancellor" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="Click to find out more">
                                        <img src="/crop/h298/w1101/1/2025/March/2.zp262889.png" class="img-fluid d-block" alt="" draggable="false">
                            <div class="container d-block">
                <div class="row">
                  <div class="offset-md-2 col-md-8 text-center"> 
                    <h1>A new chapter for UP as Professor Francis Petersen takes the helm as the 14th Vice-Chancellor</h1>
                  </div>
                </div>
              </div>
                        </a> 
                      </li>
                                                  <li class="slide-plain" style="width: 100%; float: left; margin-right: -100%; position: relative; opacity: 0; display: block; z-index: 1;" data-thumb-alt="">
                        <a class="d-block" href="https://www.up.ac.za/news/post_3295453-message-from-the-vice-chancellor-and-principal-make-today-matter-this-human-rights-day" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="Click to find out more">
                                        <img src="/crop/h298/w1101/1/2025/March/web.zp262888.jpg" class="img-fluid d-block" alt="" draggable="false">
                            <div class="container d-block">
                <div class="row">
                  <div class="offset-md-2 col-md-8 text-center"> 
                    <h1>Message from the Vice-Chancellor and Principal: Make Today Matter this Human Rights Month</h1>
                  </div>
                </div>
              </div>
                        </a> 
                      </li>
                                                  <li class="slide-plain" style="width: 100%; float: left; margin-right: -100%; position: relative; opacity: 0; display: block; z-index: 1;" data-thumb-alt="">
                        <a class="d-block" href="https://www.up.ac.za/news/post_3295067-six-up-subjects-ranked-best-in-south-africa-in-latest-qs-rankings" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="Click to find out more">
                                        <img src="/crop/h298/w1101/1/2025/March/copy-of-web-1101x298_no-logo_no-text.zp260862.png" class="img-fluid d-block" alt="" draggable="false">
                            <div class="container d-block">
                <div class="row">
                  <div class="offset-md-2 col-md-8 text-center"> 
                    <h1>Six UP subjects ranked best in South Africa in latest QS rankings</h1>
                  </div>
                </div>
              </div>
                        </a> 
                      </li>
                                                  <li class="slide-plain" style="width: 100%; float: left; margin-right: -100%; position: relative; opacity: 0; display: block; z-index: 1;" data-thumb-alt="">
                        <div class="d-block">
                                        <img src="/crop/h298/w1101/1/2025/March/untitled-1-1.zp262308.png" class="img-fluid d-block" alt="" draggable="false">
                            <div class="container d-block">
                <div class="row">
                  <div class="offset-md-2 col-md-8 text-center"> 
                    <h1>UP appoints Dr Naledi Pandor as honorary professor in education</h1>
                  </div>
                </div>
              </div>
                        </div>
                      </li>
                            </ul>
        <div class="loader" style="display: none;"><img src="/themes/up2.0/images/loading-img.png" class="img-fluid" alt="" draggable="false"><i class="fa fa-spin fa-spinner"></i></div>
      </div>
      <div class="flex-navigation container center"><ol class="flex-control-nav flex-control-paging"><li><a href="#" class="flex-active">1</a></li><li><a href="#">2</a></li><li><a href="#">3</a></li><li><a href="#">4</a></li></ol><ul class="flex-direction-nav"><li class="flex-nav-prev"><a class="flex-prev" href="#">Previous</a></li><li class="flex-nav-next"><a class="flex-next" href="#">Next</a></li></ul></div>
</section>
    <div class="content-area">
      <div class="bg-color-01 padding-top-15 padding-bottom-30">
        <div class="container">
          <h1 class="margin-bottom-25">News</h1>
          <ul class="breadcrumb">
            <li class="breadcrumb-item"><a href="https://www.up.ac.za">University of Pretoria</a></li>
            <li class="breadcrumb-item active">News</li>
          </ul>
                    <div class="row">
            <div class="col-lg-9">
              <div class="row margin-bottom-15 filters">
                <div class="col-md-12">
                  <div class="container">
                    <div class="row margin-top-15 margin-bottom-30 filter filters bg-color-08 padding-top-15 padding-bottom-15">
                      <div class="col-md-2 align-self-center">
                        <h6 class="color-05 margin-bottom-0">Filter</h6>
                      </div>
                      <div class="col-md-10">
                        <div class="row">
                          <div class="col-md-4">
                            <div class="btn-group margin-top-15-767 btn-block">
                              <button id="category-button" data-value="" type="button" class="btn btn-default dropdown-toggle btn-block" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" aria-label="Filter by category">
                                Category                              </button>
                              <ul id="category-dropdown" class="dropdown-menu dropdown-menu-right">
                                                                <li><a href="#nogo" data-value="1805127">Arts &amp; Culture</a></li>
                                                                <li><a href="#nogo" data-value="9036">Research</a></li>
                                                                <li><a href="#nogo" data-value="12">News</a></li>
                                                                <li><a href="#nogo" data-value="125">Sport &amp; Athletics</a></li>
                                                                <li><a href="#nogo" data-value="2913201">University Social Responsibility</a></li>
                                                              </ul>
                            </div>
                          </div>
                          <div class="col-md-4">
                            <div class="btn-group margin-top-15-767 btn-block">
                              <button id="year-button" data-value="" type="button" class="btn btn-default dropdown-toggle btn-block" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" aria-label="Filter by year">
                                Year                              </button>
                              <ul id="year-dropdown" class="dropdown-menu dropdown-menu-right">
                                                                <li><a href="#nogo" data-value="2025">2025</a></li>
                                                                <li><a href="#nogo" data-value="2024">2024</a></li>
                                                                <li><a href="#nogo" data-value="2023">2023</a></li>
                                                                <li><a href="#nogo" data-value="2022">2022</a></li>
                                                                <li><a href="#nogo" data-value="2021">2021</a></li>
                                                                <li><a href="#nogo" data-value="2020">2020</a></li>
                                                                <li><a href="#nogo" data-value="2019">2019</a></li>
                                                                <li><a href="#nogo" data-value="2018">2018</a></li>
                                                                <li><a href="#nogo" data-value="2017">2017</a></li>
                                                                <li><a href="#nogo" data-value="2016">2016</a></li>
                                                                <li><a href="#nogo" data-value="2015">2015</a></li>
                                                                <li><a href="#nogo" data-value="2014">2014</a></li>
                                                                <li><a href="#nogo" data-value="2013">2013</a></li>
                                                                <li><a href="#nogo" data-value="2012">2012</a></li>
                                                                <li><a href="#nogo" data-value="2011">2011</a></li>
                                                                <li><a href="#nogo" data-value="2010">2010</a></li>
                                                                <li><a href="#nogo" data-value="2009">2009</a></li>
                                                                <li><a href="#nogo" data-value="2008">2008</a></li>
                                                                <li><a href="#nogo" data-value="2007">2007</a></li>
                                                              </ul>
                            </div>
                          </div>
                          <div class="col-md-4">
                            <div class="btn-group margin-top-15-767 btn-block">
                              <button id="month-button" data-value="" type="button" class="btn btn-default dropdown-toggle btn-block" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" aria-label="Filter by month">
                                Month                              </button>
                              <ul id="month-dropdown" class="dropdown-menu dropdown-menu-right">
                                                                <li><a href="#nogo" data-value="1">January</a></li>
                                                                <li><a href="#nogo" data-value="2">February</a></li>
                                                                <li><a href="#nogo" data-value="3">March</a></li>
                                                                <li><a href="#nogo" data-value="4">April</a></li>
                                                                <li><a href="#nogo" data-value="5">May</a></li>
                                                                <li><a href="#nogo" data-value="6">June</a></li>
                                                                <li><a href="#nogo" data-value="7">July</a></li>
                                                                <li><a href="#nogo" data-value="8">August</a></li>
                                                                <li><a href="#nogo" data-value="9">September</a></li>
                                                                <li><a href="#nogo" data-value="10">October</a></li>
                                                                <li><a href="#nogo" data-value="11">November</a></li>
                                                                <li><a href="#nogo" data-value="12">December</a></li>
                                                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
                            <ul class="row news-list">
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3296210-world-water-day-every-drop-counts-on-up-campuses-">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/future-africa-rainwater-harvesting.zp262896.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 173px;">World Water Day: Every drop counts on UP campuses </h4>
                  </a>
                                                      <p><small>Posted on <strong>March 22, 2025</strong></small></p>
                                    <p>The University of Pretoria (UP) has long demonstrated its commitment to supporting the Sustainable Development Goals (SDGs) as outlined by the United Nations, particularly SDG 6: Clean Water and Sanitation. World Water Day, which is observed annually on 22 March, highlights the importance of...</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3296060-up-expert-opinion-human-rights-day-south-africas-disability-bill-should-be-accessible-to-those-who-need-it-most-writes-centre-for-human-rights-researcher">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/shutterstock_1627004164.zp262879.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 173px;">UP EXPERT OPINION: HUMAN RIGHTS DAY: South Africa’s Disability Bill should be accessible to those who need it most, writes Centre for Human Rights researcher</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 21, 2025</strong></small></p>
                                    <p>In October 2024, the South African Law Reform Commission published the Protection and Promotion of Persons with Disabilities Bill for public comment.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295453-message-from-the-vice-chancellor-and-principal-make-today-matter-this-human-rights-month">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/prof-francis-peterson.zp261590.png" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 173px;">Message from the Vice-Chancellor and Principal: Make Today Matter this Human Rights Month</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 20, 2025</strong></small></p>
                                    <p>On Human Rights Day, which is observed annually on 21 March, we reflect on the power of education and action, and the sacrifices made for freedom and dignity. </p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295828-international-day-of-happiness-research-shows-that-gratitude-increases-well-being-ups-prof-tharina-guse-">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/t-guse-1.zp262844.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">International Day of Happiness: ‘Research shows that gratitude increases well-being’ – UP’s Prof Tharina Guse </h4>
                  </a>
                                                      <p><small>Posted on <strong>March 20, 2025</strong></small></p>
                                    <p>In a world where the pursuit of happiness often takes centre stage, life’s challenges can make it hard to feel truly content. But according to Professor Tharina Guse, Head of the Department of Psychology at the University of Pretoria (UP), chasing happiness for its own sake may not be the...</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295928-upholding-human-dignity-up-students-reflect-on-human-rights-day">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/img-20240427-wa0208-byron-norval.zp262864.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">Upholding human dignity: UP students reflect on Human Rights Day</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 20, 2025</strong></small></p>
                                    <p>As South Africans observe Human Rights Day on 21 March, we pay tribute to the remarkable individuals whose sacrifices have paved the way for the freedoms we often take for granted today. But what does human rights mean to the younger generation growing up in a more democratic society? </p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295854-celebrate-human-rights-day-with-an-art-and-cuisine-experience-at-javett-up">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/2024_09_javett_art_we_the_purple_launch_2tc0817-1.zp262850.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">Celebrate Human Rights Day with an Art and Cuisine experience at Javett-UP</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 19, 2025</strong></small></p>
                                    <p>In commemoration of Human Rights Day on 21 March 2025, the Javett Art Centre at the University of Pretoria proudly presents Tour and Taste: The Purple Plate—a unique fusion of art and culinary storytelling. This immersive experience brings powerful works in We, The Purple exhibition into...</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295877-discovering-how-curiosity-meets-innovation-ups-first-science-and-engineering-open-day">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/062_eyescape_250308-copy.zp262855.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 130px;">Discovering how curiosity meets innovation – UP’s first Science and Engineering Open Day</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 19, 2025</strong></small></p>
                                    <p>The importance of pure maths and physical science was practically exhibited so that learners could realise why a critical mind is vital in an ever-changing world.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3295067-six-up-subjects-ranked-best-in-south-africa-in-latest-qs-rankings">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/170-tuks-stock-shoot-day-2.1-2025-1-1.zp262790.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 130px;">Six UP subjects ranked best in South Africa in latest QS rankings</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 17, 2025</strong></small></p>
                                    <p>PRETORIA – The 2025 QS World University Rankings by Subject, released on 12 March 2025, has ranked 16 subjects offered by the University of Pretoria (UP) among the top 450 in the world. UP’s total number of ranked subjects also increased from 19 in 2024 to 22 in 2025. </p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3294831-up-expert-opinion-international-day-for-digital-learning-up-adopts-e-community-engagement-projects-for-greater-impact">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/canva-training-for-community-members-on-the-mamelodi-campus.zp262760.jpeg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 130px;">UP EXPERT OPINION: International Day for Digital Learning: UP adopts e-community engagement projects for greater impact</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 17, 2025</strong></small></p>
                                    <p>The International Day for Digital Learning is observed annually on 19 March</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3294746-a-new-chapter-for-up-as-professor-francis-petersen-takes-the-helm-as-the-14th-vice-chancellor">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/prof-petersen-delivering-his-inaugural-address.zp262750.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">A new chapter for UP as Professor Francis Petersen takes the helm as the 14th Vice-Chancellor</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 16, 2025</strong></small></p>
                                    <p>Prof Francis Petersen was inaugurated as UP’s Vice-Chancellor and Principal on the 14th of March</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3294385-ups-prof-hettie-schnfeldt-selected-as-un-hub-chair-for-sdg-3">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/prof-hettie-schnfeldt.zp262582.png" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">UP’s Prof Hettie Schönfeldt selected as UN Hub Chair for SDG 3</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 14, 2025</strong></small></p>
                                    <p>Prof Hettie Schönfeldt was recently appointed as the Hub Chair for the United Nations 
Academic Impact Sustainable Development Goal 3 </p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3294173-up-expert-opinion-households-to-pay-more-as-government-balances-debt-and-spending">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/shutterstock_1567392661.zp262549.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">UP EXPERT OPINION: Households to pay more as government balances debt and spending</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 13, 2025</strong></small></p>
                                    <p>South African households will feel the effects of the 2025 Budget, whether in at the grocery store till, through stagnant salaries, or creeping tax burdens.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3293967-empowering-public-sector-professionals-in-the-digital-age">
                    <div class="img-block">
                        <img src="/crop/h232/w344/759/fortune.zp262529.png" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 86px;">Empowering public-sector professionals in the digital age</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 13, 2025</strong></small></p>
                                    <p>Since its launch in 2020, the fully online Postgraduate Diploma (PGDip) in Public Management, offered through UPOnline, has been steadily shaping the future of public-sector professionals. What began as a small cohort of six graduates in 2022 has grown significantly, with 87 graduates crossing...</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3293667-up-choir-tuks-camerata-to-perform-as-headline-act-at-choral-conference-in-us">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/ups-tuks-camerata-with-conductor-dr-michael-j-barret-centre.zp262477.png" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 86px;">UP choir TUKS Camerata to perform as headline act at choral conference in US</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 12, 2025</strong></small></p>
                                    <p>UP choir, TUKS Camerata, recently delivered a performance to bid farewell before heading off to the US</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3293216-up-museums-textiles-exhibit-picks-up-the-thread-of-womens-stories">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/up-bokgabo-ba-masela-exhibition-02.zp262367.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 86px;">UP Museums textiles exhibit picks up the thread of women’s stories</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 11, 2025</strong></small></p>
                                    <p>The exhibition opened to the public on 7 March and runs until 17 October 2025, and can be viewed at UP’s Bridge Gallery on Hatfield campus.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3292942-international-womens-day-progress-challenges-and-the-way-forward-for-women-in-science">
                    <div class="img-block">
                        <img src="/crop/h232/w344/8/095_eyescape.zp238004.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">International Women’s Day: Progress, challenges and the way forward for women in science</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 08, 2025</strong></small></p>
                                    <p>As a medical scientist, a professor, a mother of three, and the Deputy Dean of Research and Postgraduate Studies at Faculty of Health Sciences, University of Pretoria, I stand at the intersection of scientific excellence, leadership, and the daily realities of motherhood.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3292583-what-matters-most-to-me-is-the-impact-i-make-newly-appointed-full-professor-anneli-douglas-">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/anneli-douglas_tm-1-1-1-4.zp255010.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">‘What matters most to me is the impact I make’ – newly appointed full professor Anneli Douglas </h4>
                  </a>
                                                      <p><small>Posted on <strong>March 07, 2025</strong></small></p>
                                    <p>Congratulations to Professor Anneli Douglas of UP’s Tourism Management Division, who has been appointed as a full professor.</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3292775-tobacco-industry-targeting-africas-youth-as-new-market-warns-up-expert">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/shutterstock_2426165067.zp262306.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">Tobacco industry targeting Africa’s youth as new market, warns UP expert</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 07, 2025</strong></small></p>
                                    <p>The industry is aggressively marketing products such as e-cigarettes and other smokeless tobacco alternatives to young people in Africa</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3292720-up-appoints-dr-naledi-pandor-as-honorary-professor-in-education">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/prof-naledi-pandor-gave-an-address-at-a-ceremony-to-celebrate-her-honoraryprofessorship.zp262301.png" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">UP appoints Dr Naledi Pandor as honorary professor in education</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 06, 2025</strong></small></p>
                                    <p>UP has welcomed former cabinet minister Naledi Pandor to its Faculty of Education as an honorary professor</p>
                </li>
                                <li class="col-md-4 margin-bottom-20">
                                    <a href="https://www.up.ac.za/news/post_3292225-up-experts-and-volunteers-spearhead-first-large-scale-magaliesberg-aloe-reintroduction">
                    <div class="img-block">
                        <img src="/crop/h232/w344/1/2025/March/a-flowering-aloe-peglerae-plant.-photo-credit-kayleigh-murray.zp262042.jpg" class="img-fluid" alt="">
                    </div>
                    <h4 class="equal-height" style="height: 108px;">UP experts and volunteers spearhead first large-scale Magaliesberg aloe reintroduction</h4>
                  </a>
                                                      <p><small>Posted on <strong>March 05, 2025</strong></small></p>
                                    <p>The Magaliesberg aloe is a slow-growing species and is known for its spectacular red flowers.</p>
                </li>
                              </ul>
                            <div class="row">
                <div class="col-12 col-sm-12 col-md-12 align-self-center">
                  <nav>
                  <div class="zp_pager clearfix"><div class="zp_pager_results"></div><div class="zp_pager_links"><ul class="pagination"> <li class="page-item active"><a class="page-link active" href="#nogo">1</a></li>  <li class="page-item"><a class="page-link jscroll-next" href="/news?zpage=2">2</a></li>  <li class="page-item"><a class="page-link jscroll-next" href="/news?zpage=3">3</a></li>  <li class="page-item"><a class="page-link jscroll-next" href="/news?zpage=4">4</a></li>  <li class="page-item"><a class="page-link jscroll-next" href="/news?zpage=5">5</a></li> <li class="page-item disabled"><a class="page-link">...</a></li><li class="next"><a class="page-link" href="/news?zpage=2"><span aria-hidden="true">›</span></a></li> <li class="last"><a class="page-link" href="/news?zpage=354"><span aria-hidden="true">»</span></a></li> </ul></div></div>                  </nav>
                </div>
              </div>
            </div>
			      <div class="col-lg-3 rightbar related  padding-top-15">
              <h4 class="color-05">News Categories</h4>
              <hr class="margin-top-0 margin-bottom-10 border">
              <ul class="list-unstyled">
                                <li><a class="center-block padding-bottom-5 color-05" href="https://www.up.ac.za/news/category_1805127-arts-culture">Arts &amp; Culture</a></li>
                                <li><a class="center-block padding-bottom-5 color-05" href="https://www.up.ac.za/news/category_9036-research">Research</a></li>
                                <li><a class="center-block padding-bottom-5 color-05" href="https://www.up.ac.za/news/category_12-news">News</a></li>
                                <li><a class="center-block padding-bottom-5 color-05" href="https://www.up.ac.za/news/category_125-sport-athletics">Sport &amp; Athletics</a></li>
                                <li><a class="center-block padding-bottom-5 color-05" href="https://www.up.ac.za/news/category_2913201-university-social-responsibility">University Social Responsibility</a></li>
                              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
</div><div class="footer-area">
      <div class="container">
        <div class="row">
          <div class="col-md-4">
            <p>
              <strong>Postal Address:</strong><br>
              <span>University of Pretoria</span><br>
              <span>Private Bag x 20</span><br>
              <span>Hatfield</span><br>
              <span>0028</span><br>
            </p>
            <p>
              <strong>Location:</strong><br>
              <span>
                <a class="color-01" href="/article/2749435/campuses-maps-directions">GIBS</a> | 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Groenkloof</a> | 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Hatfield</a><br> 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Hillcrest</a> | 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Mamelodi</a> | 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Onderstepoort</a> | 
                <a class="color-01" href="/article/2749435/campuses-maps-directions">Prinshof</a>
              </span>
            </p>
          </div>
          <div class="col-md-4">
            <p>
              <strong>Student Service Centre (for Contact students):</strong><br>
              <span>Contact Centre - Telephone:&nbsp;012&nbsp;420&nbsp;3111</span><br>
              <span>Contact Centre - Email:&nbsp;<a class="color-01" href="mailto:ssc@up.ac.za">ssc@up.ac.za</a></span>
            </p>
          </div>
          <section id="social_menu" class="zp-block-frontpageblock-social_menu col-md-4">
                          <p><strong>Get Social With Us</strong></p>
              <p class="social-links">
                                                                                                <a class="fb" target="_blank" href="https://www.facebook.com/UnivofPretoria/" aria-label="Facebook">
                                                      <i class="fa fa-facebook"></i>
                                                  </a>
                                                                                                    <a class="yt" target="_blank" href="https://www.youtube.com/user/UPvideolibrary?ob=0&amp;feature=results_main" aria-label="YouTube">
                                                      <i class="fa fa-youtube-play"></i>
                                                  </a>
                                                                                                                                                            <a class="in" target="_blank" href="https://www.instagram.com/universityofpretoria/" aria-label="Instagram">
                                                      <i class="fa fa-instagram"></i>
                                                  </a>
                                                                                                    <a class="li" target="_blank" href="https://www.linkedin.com/company/university-of-pretoria" aria-label="LinkedIn">
                                                      <i class="fa fa-linkedin"></i>
                                                  </a>
                                                                                                    <a class="tw" target="_blank" href="https://twitter.com/uptuks" aria-label="Twitter">
                                                      <i></i>
                                                  </a>
                                                                                                    <a class="tt" target="_blank" href="https://www.tiktok.com/@univofpretoria?lang=en" aria-label="TikTok">
                                                      <i></i>
                                                  </a>
                                                  </p>
            <p><strong>Download the UP Mobile App</strong></p>
            <p class="mobile-app-downloads">
                <a href="https://play.google.com/store/apps/details?id=za.ac.up.m" target="_blank"><img src="/themes/up2.0/images/google-play-badge.png" height="60" alt=""></a>
                <a href="https://apps.apple.com/za/app/up-mobile-app/id1467791140" target="_blank"><img src="/themes/up2.0/images/apple-store-badge.png" width="140" height="40" alt=""></a>
            </p>
</section>
        </div>
      </div>
    </div><div class="socket-area">
      <div class="container">
        <div class="row">
          <div class="col-xl-4">
            <p class="margin-0 padding-bottom-15 text-center text-xl-left">Copyright © University of Pretoria 2025. All rights reserved.</p>
          </div>
          <div class="col-xl-8">
            <p class="margin-0 padding-bottom-15 text-center text-xl-right">
              <a class="text-nowrap" href="/human-resources-department/article/257103/careersup">Careers@UP</a> | 
              <a class="text-nowrap" href="/tender">Tenders@UP</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/article/2806555/ethics-hotline">Ethics Hotline</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/iGaPP-programme/article/2720063/access-to-information">PAIA Manual</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/iGaPP-programme/article/2820008/privacy-notices">Privacy Notices</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/web-office/article/2884659/website-privacy-notice">Website Privacy Notice</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/web-office/article/2895058/disclaimer">Disclaimer</a> | 
              <a class="text-nowrap" href="https://www.up.ac.za/web-office/article/2882822/terms-of-use-website">Terms of use</a>
            </p>
          </div>
        </div>
      </div>
    </div><div class="notice-area border-0"></div><div class="modal fade" id="generalModal" tabindex="-1" role="dialog" aria-labelledby="" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"></h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">×</span>
            </button>
          </div>
          <div class="modal-body"></div>
        </div>
      </div>
    </div><div class="modal fade" id="socialModal" tabindex="-1" role="dialog" aria-labelledby="" aria-hidden="true">
      <div class="modal-dialog modal-sm modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Share</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">×</span>
            </button>
          </div>
          <div class="modal-body social-links social-links-modal text-center">
            <a class="fb margin-bottom-none" target="_blank" href="https://www.facebook.com/sharer.php?u=https%3A%2F%2Fwww.up.ac.za%2Fnews" aria-label="Facebook"><i class="fa fa-facebook"><span class="sr-only">Facebook</span></i></a>
            <a class="li margin-bottom-0" target="_blank" href="https://linkedin.com/shareArticle?mini=true&amp;url=https%3A%2F%2Fwww.up.ac.za%2Fnews" aria-label="LinkedIn"><i class="fa fa-linkedin"><span class="sr-only">LinkedIn</span></i></a>
            <a class="tw margin-bottom-0" target="_blank" href="https://twitter.com/share?url=https%3A%2F%2Fwww.up.ac.za%2Fnews" aria-label="Twitter"><i><span class="sr-only">Twitter</span></i></a>
            <a class="ma margin-bottom-0" href="mailto:?body=https%3A%2F%2Fwww.up.ac.za%2Fnews"><i class="fa fa-envelope" aria-label="Email Us"><span class="sr-only">Email Us</span></i></a>
            <a class="wa margin-bottom-0" target="_blank" href="https://api.whatsapp.com/send?text=https%3A%2F%2Fwww.up.ac.za%2Fnews" aria-label="WhatsApp"><i class="fa fa-whatsapp"><span class="sr-only">WhatsApp</span></i></a>
          </div>
        </div>
      </div>
    </div><div class="accessibility">
      <a href="#nogo" aria-label="Accessibility" role="heading" aria-level="3"><span class="access-btn"><i class="fa fa-wheelchair-alt"></i><i class="fa fa-close d-none"></i></span></a>
      <div class="access-inner">
        <ul class="fa-ul margin-bottom-0">
          <li><i class="fa fa-li fa-search-plus"></i><a class="font-button increase font-increase-1" href="#nogo" aria-label="Increase Text">Increase Text</a></li>
          <li><i class="fa fa-li fa-search-minus"></i><a class="font-button decrease" href="#nogo" aria-label="Decrease Text">Decrease Text</a></li>
          <li><i class="fa fa-li fa-link"></i><a class="underline-links" href="#nogo" aria-label="Links Underline">Links Underline</a></li>
          <li><i class="fa fa-li fa-font"></i><a class="reader-view" href="#nogo" aria-label="Reader View">Reader View</a></li>
          <li><i class="fa fa-li fa-repeat"></i><a class="access-reset" href="#nogo" aria-label="Reset">Reset</a></li>
        </ul>
      </div>
    </div><div class="float-buttons float-buttons-additional">
    <a href="/faq" class="btn faq" aria-label="FAQ's"><i class="fa fa-question-circle"></i> FAQ's</a>
      <a href="/feedback/request" class="btn email" aria-label="Email Us"><i class="fa fa-envelope"></i> Email Us</a>
      <a href="https://virtualcampus.up.ac.za" target="_blank" class="btn campus" aria-label="Virtual Campus"><img src="/themes/up2.0/images/360-ico.png" alt=""> Virtual Campus</a>
      <a href="#nogo" target="_blank" class="btn share" data-toggle="modal" data-target="#socialModal" aria-label="Share"><i class="fa fa-share-alt"></i> Share</a>
      <a href="#nogo" class="btn cookie-preferences-btn"><i class="fa fa-cog"></i> Cookie Preferences</a>
            <a href="https://upnet.up.ac.za/donate/signon.html" target="_blank" class="btn welcome-link"><img src="/themes/up2.0/images/giving-campaign-button.png" alt=""></a>
          </div><div id="topcontrol" title="Scroll Back to Top" style="position: fixed; bottom: 0px; right: 10px; cursor: pointer; opacity: 0;"><i class="fa fa-chevron-up"></i></div></div>
<div id="mm-blocker" class="mm-slideout"></div>
```
