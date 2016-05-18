var parsleyOptions = {
  errorClass: 'error',
  focus: 'none',
  errorsWrapper: '<span></span>',
  errorTemplate: '<span class="error active"></span>',
  excluded: 'input[type=button], input[type=submit], input[type=reset], div.selectize-input input'
};
var currentYear = new Date().getFullYear();
var schoolOptions = [
    {value: "University of Illinois - Urbana-Champaign", name: "University of Illinois at Urbana-Champaign", search: ['UIUC']},
    {value: "Arizona State University", name: "Arizona State University", search: ['ASU']},
    {value: "Ball State University", name: "Ball State University", search: ['BSU']},
    {value: "Binghamton University", name: "Binghamton University", search: ['BU']},
    {value: "Boston University", name: "Boston University", search: ['BU']},
    {value: "Bowling Green State University", name: "Bowling Green State University", search: ['BGSU']},
    {value: "Bradley University", name: "Bradley University", search: ['BU']},
    {value: "Brown University", name: "Brown University", search: ['BU']},
    {value: "Butler University", name: "Butler University", search: ['BU']},
    {value: "California Institute of Technology", name: "California Institute of Technology", search: ['CIOT', 'CIT']},
    {value: "Carnegie Mellon University", name: "Carnegie Mellon University", search: ['CMU']},
    {value: "Carthage College", name: "Carthage College", search: ['CC']},
    {value: "Case Western Reserve University", name: "Case Western Reserve University", search: ['CWRU']},
    {value: "College of Dupage", name: "College of Dupage", search: ['COD']},
    {value: "Colorado State University", name: "Colorado State University", search: ['CSU']},
    {value: "Columbia College Chicago", name: "Columbia College Chicago", search: ['CCC']},
    {value: "Columbia University", name: "Columbia University", search: ['CU']},
    {value: "Concordia University Wisconsin", name: "Concordia University Wisconsin", search: ['CUW']},
    {value: "Cornell University", name: "Cornell University", search: ['CU']},
    {value: "Depaul University", name: "Depaul University", search: ['DU']},
    {value: "Depauw University", name: "Depauw University", search: ['DU']},
    {value: "Drake University", name: "Drake University", search: ['DU']},
    {value: "Drexel University", name: "Drexel University", search: ['DU']},
    {value: "Duke University", name: "Duke University", search: ['DU']},
    {value: "Emory University", name: "Emory University", search: ['EU']},
    {value: "Florida State University", name: "Florida State University", search: ['FSU']},
    {value: "George Mason University", name: "George Mason University", search: ['GMU']},
    {value: "Georgia Institute of Technology", name: "Georgia Institute of Technology", search: ['GIOT', 'GIT']},
    {value: "Grinnell College", name: "Grinnell College", search: ['GC']},
    {value: "Harper College", name: "Harper College", search: ['HC']},
    {value: "Harvard University", name: "Harvard University", search: ['HU']},
    {value: "Illinois Institute of Technology", name: "Illinois Institute of Technology", search: ['IIOT', 'IIT']},
    {value: "Illinois State University", name: "Illinois State University", search: ['ISU']},
    {value: "Indiana Institute of Technology", name: "Indiana Institute of Technology", search: ['IIOT','IIT']},
    {value: "Indiana University - Purdue University Indianapolis", name: "Indiana University - Purdue University Indianapolis", search: ['IU', 'PUI']},
    {value: "Indiana University - Bloomington", name: "Indiana University - Bloomington", search: ['IUB']},
    {value: "Iowa State University", name: "Iowa State University", search: ['ISU']},
    {value: "Kent State University", name: "Kent State University", search: ['KSU']},
    {value: "Louisiana State University", name: "Louisiana State University", search: ['LSU']},
    {value: "Macalester College", name: "Macalester College", search: ['MC']},
    {value: "Marquette University", name: "Marquette University", search: ['MU']},
    {value: "Massachusetts Institute of Technology (MIT)", name: "Massachusetts Institute of Technology (MIT)", search: ['MIOT', 'MIT']},
    {value: "Miami University", name: "Miami University", search: ['MU']},
    {value: "Michigan Technologlical University", name: "Michigan Technologlical University", search: ['MTU']},
    {value: "Michigan State University", name: "Michigan State University", search: ['MSU', 'MU']},
    {value: "Milwaukee School of Engineering", name: "Milwaukee School of Engineering", search: ['MSOE', 'MSE']},
    {value: "Missouri University of Science and Technology", name: "Missouri University of Science and Technology", search: ['MUOSAT', 'MUST']},
    {value: "New York University", name: "New York University", search: ['NYU']},
    {value: "Northeastern Illinois University", name: "Northeastern Illinois University", search: ['NIU']},
    {value: "Northern Illinois University", name: "Northern Illinois University", search: ['NIU']},
    {value: "Northwestern University", name: "Northwestern University", search: ['NU']},
    {value: "Notre Dame University", name: "Notre Dame University", search: ['NDU']},
    {value: "Oakton Community College", name: "Oakton Community College", search: ['OCC']},
    {value: "Oberlin College", name: "Oberlin College", search: ['OC']},
    {value: "Ohio State University", name: "Ohio State University", search: ['OSU', 'OU']},
    {value: "Ohio University", name: "Ohio University", search: ['OU']},
    {value: "Pennsylvania State University", name: "Pennsylvania State University", search: ['PSU', 'PU']},
    {value: "Princeton University", name: "Princeton University", search: ['PU']},
    {value: "Purdue University", name: "Purdue University", search: ['PU']},
    {value: "Rensselaer Polytechnic Institute", name: "Rensselaer Polytechnic Institute", search: ['RPI']},
    {value: "Rhode Island School of Design", name: "Rhode Island School of Design", search: ['RISOD', 'RISD']},
    {value: "Rice University", name: "Rice University", search: ['RU']},
    {value: "Rose-Hulman Institute of Technology", name: "Rose-Hulman Institute of Technology", search: ['RHIOT', 'RHIT']},
    {value: "Rutgers University", name: "Rutgers University", search: ['RU']},
    {value: "Southern Connecticut State University", name: "Southern Connecticut State University", search: ['SCSU']},
    {value: "Southern Illinois University - Carbondale", name: "Southern Illinois University - Carbondale", search: ['SIUC']},
    {value: "Southern Illinois University - Edwardsville", name: "Southern Illinois University - Edwardsville", search: ['SIUE']},
    {value: "St. Louis University", name: "St. Louis University", search: ['SLU']},
    {value: "Stanford University", name: "Stanford University", search: ['SU']},
    {value: "Texas A&M University", name: "Texas A&M University", search: ['TAMU', 'TU']},
    {value: "University of Buffalo", name: "University of Buffalo", search: ['UOB', 'UB']},
    {value: "University of California - Berkeley", name: "University of California - Berkeley", search: ['UOCB', 'UCB']},
    {value: "University of Central Florida", name: "University of Central Florida", search: ['UOCF', 'UCF', 'UF']},
    {value: "University of Chicago", name: "University of Chicago", search: ['UC']},
    {value: "University of Cincinnati", name: "University of Cincinnati", search: ['UOC', 'UC']},
    {value: "University of Colorado - Boulder", name: "University of Colorado - Boulder", search: ['UOCB', 'UCB']},
    {value: "University of Dayton", name: "University of Dayton", search: ['UOD', 'UD']},
    {value: "University of Georgia", name: "University of Georgia", search: ['UOG', 'UG']},
    {value: "University of Illinois - Chicago", name: "University of Illinois - Chicago", search: ['UOIC', 'UIC']},
    {value: "University of Illinois - Springfield", name: "University of Illinois - Springfield", search: ['UOIS', 'UIS']},
    {value: "University of Iowa", name: "University of Iowa", search: ['UOI', 'UI']},
    {value: "University of Maryland", name: "University of Maryland", search: ['UOM', 'UM']},
    {value: "University of Michigan - Ann Arbor", name: "University of Michigan - Ann Arbor", search: ['UOM', 'UM']},
    {value: "University of Minnesota - Twin Cities", name: "University of Minnesota - Twin Cities", search: ['UOM', 'UM']},
    {value: "University of Missouri", name: "University of Missouri", search: ['UOM', 'UM', 'Mizzou']},
    {value: "University of Nebraska - Lincoln", name: "University of Nebraska - Lincoln", search: ['UONL', 'UNL']},
    {value: "University of Pennsylvania", name: "University of Pennsylvania", search: ['UOP', 'UP']},
    {value: "University of Pittsburgh", name: "University of Pittsburgh", search: ['UOP', 'UP']},
    {value: "University of Texas - Austin", name: "University of Texas - Austin", search: ['UOTA', 'UTA']},
    {value: "University of Toledo", name: "University of Toledo", search: ['UOT', 'UT']},
    {value: "University of Toronto", name: "University of Toronto", search: ['UOT', 'UT']},
    {value: "University of Washington", name: "University of Washington", search: ['UW']},
    {value: "University of Wisconsin - Madison", name: "University of Wisconsin - Madison", search: ['UOWM', 'UWM']},
    {value: "University of Wisconsin - Milwaukee", name: "University of Wisconsin - Milwaukee", search: ['UOWM', 'UWM']},
    {value: "University of Pittsburgh", name: "University of Pittsburgh", search: ['UOP', 'UP']},
    {value: "Vanderbilt University", name: "Vanderbilt University", search: ['VU']},
    {value: "Virginia Institute of Technology", name: "Virginia Institute of Technology", search: ['VIOT', 'VIT']},
    {value: "Virginia Polytechnic Institute and State University (Virginia Tech)", name: "Virginia Polytechnic Institute and State University (Virginia Tech)", search: ['VT']},
    {value: "Washington University in St. Louis", name: "Washington University in St. Louis", search: ['WUIST', 'WUST']},
    {value: "Worcester Polytechnic Institute", name: "Worcester Polytechnic Institute", search: ['WPI', 'WI']},
    {value: "Wright State University", name: "Wright State University", search: ['WSU']},
    {value: "Yale University", name: "Yale University", search: ['YU']},
];
var majorOptions = [
    {value: "CS", name: "Computer Science"},
    {value: "ECE", name: "Electrical And Computer Engineering"},
    {value: "CE", name: "Computer Engineering"},
    {value: "Design", name: "Design"},
    {value: "MechE", name: "Mechanical Engineering", search: ["Mech E"]},
    {value: "IT", name: "Information Technology"},
    {value: "GA", name: "General Agriculture"},
    {value: "APAM", name: "Agriculture Production And Management"},
    {value: "AE", name: "Agricultural Economics"},
    {value: "AS", name: "Animal Sciences"},
    {value: "FS", name: "Food Science"},
    {value: "PSAA", name: "Plant Science And Agronomy"},
    {value: "SS", name: "Soil Science"},
    {value: "MA", name: "Miscellaneous Agriculture"},
    {value: "F", name: "Forestry"},
    {value: "NRM", name: "Natural Resources Management"},
    {value: "FA", name: "Fine Arts"},
    {value: "DATA", name: "Drama And Theater Arts"},
    {value: "M", name: "Music"},
    {value: "VAPA", name: "Visual And Performing Arts"},
    {value: "CAAGD", name: "Commercial Art And Graphic Design"},
    {value: "FVAPA", name: "Film Video And Photographic Arts"},
    {value: "SA", name: "Studio Arts"},
    {value: "MFA", name: "Miscellaneous Fine Arts"},
    {value: "ES", name: "Environmental Science"},
    {value: "B", name: "Biology"},
    {value: "BS", name: "Biochemical Sciences"},
    {value: "B", name: "Botany"},
    {value: "MB", name: "Molecular Biology"},
    {value: "E", name: "Ecology"},
    {value: "G", name: "Genetics"},
    {value: "M", name: "Microbiology"},
    {value: "P", name: "Pharmacology"},
    {value: "P", name: "Physiology"},
    {value: "Z", name: "Zoology"},
    {value: "N", name: "Neuroscience"},
    {value: "MB", name: "Miscellaneous Biology"},
    {value: "CSAB", name: "Cognitive Science And Biopsychology"},
    {value: "GB", name: "General Business"},
    {value: "A", name: "Accounting"},
    {value: "AS", name: "Actuarial Science"},
    {value: "BMAA", name: "Business Management And Administration"},
    {value: "OLAE", name: "Operations Logistics And E-Commerce"},
    {value: "BE", name: "Business Economics"},
    {value: "MAMR", name: "Marketing And Marketing Research"},
    {value: "F", name: "Finance"},
    {value: "HRAPM", name: "Human Resources And Personnel Management"},
    {value: "IB", name: "International Business"},
    {value: "HM", name: "Hospitality Management"},
    {value: "MISAS", name: "Management Information Systems And Statistics"},
    {value: "MB&MA", name: "Miscellaneous Business & Medical Administration"},
    {value: "C", name: "Communications"},
    {value: "J", name: "Journalism"},
    {value: "MM", name: "Mass Media"},
    {value: "AAPR", name: "Advertising And Public Relations"},
    {value: "CT", name: "Communication Technologies"},
    {value: "CAIS", name: "Computer And Information Systems"},
    {value: "CPADP", name: "Computer Programming And Data Processing"},
    {value: "IS", name: "Information Sciences"},
    {value: "CAMAS", name: "Computer Administration Management And Security"},
    {value: "CNAT", name: "Computer Networking And Telecommunications"},
    {value: "M", name: "Mathematics"},
    {value: "AM", name: "Applied Mathematics"},
    {value: "SADS", name: "Statistics And Decision Science"},
    {value: "MACS", name: "Mathematics And Computer Science"},
    {value: "GE", name: "General Education"},
    {value: "EAAS", name: "Educational Administration And Supervision"},
    {value: "SSC", name: "School Student Counseling"},
    {value: "EE", name: "Elementary Education"},
    {value: "MTE", name: "Mathematics Teacher Education"},
    {value: "PAHET", name: "Physical And Health Education Teaching"},
    {value: "ECE", name: "Early Childhood Education"},
    {value: "SACTE", name: "Science And Computer Teacher Education"},
    {value: "STE", name: "Secondary Teacher Education"},
    {value: "SNE", name: "Special Needs Education"},
    {value: "SSOHTE", name: "Social Science Or History Teacher Education"},
    {value: "TEML", name: "Teacher Education: Multiple Levels"},
    {value: "LADE", name: "Language And Drama Education"},
    {value: "AAME", name: "Art And Music Education"},
    {value: "ME", name: "Miscellaneous Education"},
    {value: "LS", name: "Library Science"},
    {value: "A", name: "Architecture"},
    {value: "GE", name: "General Engineering"},
    {value: "AE", name: "Aerospace Engineering"},
    {value: "BE", name: "Biological Engineering"},
    {value: "AE", name: "Architectural Engineering"},
    {value: "BE", name: "Biomedical Engineering"},
    {value: "CE", name: "Chemical Engineering"},
    {value: "CE", name: "Civil Engineering"},
    {value: "EE", name: "Electrical Engineering"},
    {value: "EMPAS", name: "Engineering Mechanics Physics And Science"},
    {value: "EE", name: "Environmental Engineering"},
    {value: "GAGE", name: "Geological And Geophysical Engineering"},
    {value: "IAME", name: "Industrial And Manufacturing Engineering"},
    {value: "MEAMS", name: "Materials Engineering And Materials Science"},
    {value: "ME", name: "Metallurgical Engineering"},
    {value: "MAME", name: "Mining And Mineral Engineering"},
    {value: "NAAME", name: "Naval Architecture And Marine Engineering"},
    {value: "NE", name: "Nuclear Engineering"},
    {value: "PE", name: "Petroleum Engineering"},
    {value: "ME", name: "Miscellaneous Engineering"},
    {value: "ET", name: "Engineering Technologies"},
    {value: "EAIM", name: "Engineering And Industrial Management"},
    {value: "EET", name: "Electrical Engineering Technology"},
    {value: "IPT", name: "Industrial Production Technologies"},
    {value: "MechERT", name: "Mechanical Engineering Related Technologies", search: ["Mech ERT"]},
    {value: "MET", name: "Miscellaneous Engineering Technologies"},
    {value: "MS", name: "Materials Science"},
    {value: "NS", name: "Nutrition Sciences"},
    {value: "GMAHS", name: "General Medical And Health Services"},
    {value: "CDSAS", name: "Communication Disorders Sciences And Services"},
    {value: "HAMAS", name: "Health And Medical Administrative Services"},
    {value: "MAS", name: "Medical Assisting Services"},
    {value: "MTT", name: "Medical Technologies Technicians"},
    {value: "HAMPP", name: "Health And Medical Preparatory Programs"},
    {value: "N", name: "Nursing"},
    {value: "PPSAA", name: "Pharmacy Pharmaceutical Sciences And Administration"},
    {value: "TTP", name: "Treatment Therapy Professions"},
    {value: "CAPH", name: "Community And Public Health"},
    {value: "MHMP", name: "Miscellaneous Health Medical Professions"},
    {value: "AEACS", name: "Area Ethnic And Civilization Studies"},
    {value: "LACLAL", name: "Linguistics And Comparative Language And Literature"},
    {value: "FGLAOCFLS", name: "French German Latin And Other Common Foreign Language Studies"},
    {value: "OFL", name: "Other Foreign Languages"},
    {value: "ELAL", name: "English Language And Literature"},
    {value: "CAR", name: "Composition And Rhetoric"},
    {value: "LA", name: "Liberal Arts"},
    {value: "H", name: "Humanities"},
    {value: "IAIS", name: "Intercultural And International Studies"},
    {value: "PARS", name: "Philosophy And Religious Studies"},
    {value: "TARV", name: "Theology And Religious Vocations"},
    {value: "AAA", name: "Anthropology And Archeology"},
    {value: "AHAC", name: "Art History And Criticism"},
    {value: "H", name: "History"},
    {value: "USH", name: "United States History"},
    {value: "CSACA", name: "Cosmetology Services And Culinary Arts"},
    {value: "FACS", name: "Family And Consumer Sciences"},
    {value: "MT", name: "Military Technologies"},
    {value: "PFPRAL", name: "Physical Fitness Parks Recreation And Leisure"},
    {value: "CS", name: "Construction Services"},
    {value: "TSAT", name: "Transportation Sciences And Technologies"},
    {value: "MS", name: "Multi/Interdisciplinary Studies"},
    {value: "CR", name: "Court Reporting"},
    {value: "PALS", name: "Pre-Law And Legal Studies"},
    {value: "CJAFP", name: "Criminal Justice And Fire Protection"},
    {value: "PA", name: "Public Administration"},
    {value: "PP", name: "Public Policy"},
    {value: "PS", name: "Physical Sciences"},
    {value: "AAA", name: "Astronomy And Astrophysics"},
    {value: "ASAM", name: "Atmospheric Sciences And Meteorology"},
    {value: "C", name: "Chemistry"},
    {value: "GAES", name: "Geology And Earth Science"},
    {value: "G", name: "Geosciences"},
    {value: "O", name: "Oceanography"},
    {value: "P", name: "Physics"},
    {value: "MOGS", name: "Multi-Disciplinary Or General Science"},
    {value: "NABT", name: "Nuclear And Biological Technologies"},
    {value: "P", name: "Psychology"},
    {value: "EP", name: "Educational Psychology"},
    {value: "CP", name: "Clinical Psychology"},
    {value: "CP", name: "Counseling Psychology"},
    {value: "IAOP", name: "Industrial And Organizational Psychology"},
    {value: "SP", name: "Social Psychology"},
    {value: "MP", name: "Miscellaneous Psychology"},
    {value: "HSACO", name: "Human Services And Community Organization"},
    {value: "SW", name: "Social Work"},
    {value: "ISS", name: "Interdisciplinary Social Sciences"},
    {value: "GSS", name: "General Social Sciences"},
    {value: "E", name: "Economics"},
    {value: "C", name: "Criminology"},
    {value: "G", name: "Geography"},
    {value: "IR", name: "International Relations"},
    {value: "PSAG", name: "Political Science And Government"},
    {value: "S", name: "Sociology"},
    {value: "MSS", name: "Miscellaneous Social Sciences"}
];
var genderOptions = [
  {value: 'MALE', name: "Male"},
  {value: 'FEMALE', name: "Female"},
  {value: 'NON_BINARY', name: "Non-binary"},
  {value: 'OTHER', name: "Other"},
  {value: 'NONE', name: "Prefer not to answer"}
];
var dietOptions = [
  {value: 'GLUTEN_FREE', name: "Gluten Free"},
  {value: 'VEGETARIAN', name: "Vegetarian"},
  {value: 'VEGAN', name: "Vegan"},
  {value: 'NONE', name: "No Diet"}
];
var shirtOptions = [
  {value:'XS', name: "Extra Small"},
  {value:'S', name: "Small"},
  {value:'M', name: "Medium"},
  {value:'L', name: "Large"},
  {value:'XL', name: "Extra Large"}
];
var professionalOptions = [
  {value:'FULL_TIME', name: "Full Time"},
  {value:'INTERNSHIP', name: "Internship"},
  {value:'BOTH', name: "Both"},
  {value:'NONE', name: "None"}
];
var hackathonAttendanceOptions = [
  {value:'0', name: "None"},
  {value:'1-5', name: "A few (1-5)"},
  {value:'5+', name: "A lot (5+)"}
];
var yesNoOptions = [
  {value:'YES', name: 'Yes'},
  {value:'NO', name: 'No'},
  {value:'MAYBE', name: 'Maybe'}
];
var graduationYearOptions = [];
for (var year = 1969; year <= currentYear + 5; year++) {
  graduationYearOptions.push({ 'value': year });
}