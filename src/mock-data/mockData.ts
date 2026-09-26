// SAHAAY Mock Data - Realistic Indian Healthcare Data
export const patients = [
  { id: 'P001', name: 'Rahul Sharma', age: 34, gender: 'Male', bloodGroup: 'B+', phone: '+91 98765 43210', location: 'Chandrapur, Assam', emergencyContact: 'Priya Sharma (+91 98765 43211)', status: 'active', registeredDate: '2026-08-01', avatar: 'RS' },
  { id: 'P002', name: 'Ananya Das', age: 28, gender: 'Female', bloodGroup: 'O+', phone: '+91 98765 43220', location: 'Sonapur, Assam', emergencyContact: 'Rakesh Das (+91 98765 43221)', status: 'active', registeredDate: '2026-08-05', avatar: 'AD' },
  { id: 'P003', name: 'Priya Devi', age: 45, gender: 'Female', bloodGroup: 'A+', phone: '+91 98765 43230', location: 'Goalpara, Assam', emergencyContact: 'Amit Devi (+91 98765 43231)', status: 'active', registeredDate: '2026-08-10', avatar: 'PD' },
  { id: 'P004', name: 'Amit Kumar', age: 52, gender: 'Male', bloodGroup: 'AB+', phone: '+91 98765 43240', location: 'Nagaon, Assam', emergencyContact: 'Sunita Kumar (+91 98765 43241)', status: 'active', registeredDate: '2026-08-12', avatar: 'AK' },
  { id: 'P005', name: 'Rakesh Singh', age: 19, gender: 'Male', bloodGroup: 'B-', phone: '+91 98765 43250', location: 'Jorhat, Assam', emergencyContact: 'Meena Singh (+91 98765 43251)', status: 'active', registeredDate: '2026-08-15', avatar: 'RS' },
  { id: 'P006', name: 'Sunita Boro', age: 31, gender: 'Female', bloodGroup: 'O-', phone: '+91 98765 43260', location: 'Kokrajhar, Assam', emergencyContact: 'Dinesh Boro (+91 98765 43261)', status: 'active', registeredDate: '2026-08-18', avatar: 'SB' },
  { id: 'P007', name: 'Dipak Gogoi', age: 67, gender: 'Male', bloodGroup: 'A-', phone: '+91 98765 43270', location: 'Dibrugarh, Assam', emergencyContact: 'Parul Gogoi (+91 98765 43271)', status: 'followup', registeredDate: '2026-07-20', avatar: 'DG' },
  { id: 'P008', name: 'Mamta Kumari', age: 24, gender: 'Female', bloodGroup: 'B+', phone: '+91 98765 43280', location: 'Tezpur, Assam', emergencyContact: 'Vikram Kumari (+91 98765 43281)', status: 'active', registeredDate: '2026-08-22', avatar: 'MK' },
];

export const doctors = [
  { id: 'D001', name: 'Dr. Ananya Sharma', speciality: 'General Physician', facility: 'PHC Chandrapur', phone: '+91 98760 10001', experience: '12 years', rating: 4.8, patientsToday: 12, available: true, avatar: 'AS' },
  { id: 'D002', name: 'Dr. Arjun Das', speciality: 'Cardiologist', facility: 'District Hospital Guwahati', phone: '+91 98760 10002', experience: '18 years', rating: 4.9, patientsToday: 8, available: true, avatar: 'AD' },
  { id: 'D003', name: 'Dr. Priya Singh', speciality: 'Pediatrician', facility: 'CHC Sonapur', phone: '+91 98760 10003', experience: '8 years', rating: 4.7, patientsToday: 15, available: false, avatar: 'PS' },
  { id: 'D004', name: 'Dr. Ramesh Gupta', speciality: 'Orthopedic', facility: 'District Hospital Guwahati', phone: '+91 98760 10004', experience: '22 years', rating: 4.6, patientsToday: 10, available: true, avatar: 'RG' },
  { id: 'D005', name: 'Dr. Sunita Reddy', speciality: 'Gynecologist', facility: 'PHC Chandrapur', phone: '+91 98760 10005', experience: '15 years', rating: 4.8, patientsToday: 9, available: true, avatar: 'SR' },
  { id: 'D006', name: 'Dr. Vikram Patel', speciality: 'Dermatologist', facility: 'CHC Sonapur', phone: '+91 98760 10006', experience: '10 years', rating: 4.5, patientsToday: 7, available: true, avatar: 'VP' },
];

export const facilities = [
  { id: 'F001', name: 'PHC Chandrapur', type: 'Primary Health Centre', distance: 2.4, services: ['General Consultation', 'Basic Diagnostics', 'Maternal Care', 'Child Care'], doctorsAvailable: 3, waitingTime: 18, diagnostics: ['Blood Test', 'Urine Test', 'Basic Imaging'], medicines: 'Available', emergency: true, beds: 10, occupancy: 65, lat: 26.1445, lng: 91.7362 },
  { id: 'F002', name: 'CHC Sonapur', type: 'Community Health Centre', distance: 8.1, services: ['General Consultation', 'Specialist Consultation', 'Diagnostics', 'Maternal Care', 'Emergency'], doctorsAvailable: 6, waitingTime: 32, diagnostics: ['Blood Test', 'X-Ray', 'ECG', 'Ultrasound'], medicines: 'Available', emergency: true, beds: 30, occupancy: 72, lat: 26.1200, lng: 91.7000 },
  { id: 'F003', name: 'District Hospital Guwahati', type: 'District Hospital', distance: 22.5, services: ['All Specialities', 'Advanced Diagnostics', 'Surgery', 'ICU', 'Emergency', 'Blood Bank'], doctorsAvailable: 18, waitingTime: 45, diagnostics: ['Full Blood Panel', 'CT Scan', 'X-Ray', 'MRI', 'ECG', 'Ultrasound'], medicines: 'Available', emergency: true, beds: 200, occupancy: 81, lat: 26.1445, lng: 91.7362 },
  { id: 'F004', name: 'Rural Health Centre Dhekiajuli', type: 'Rural Health Centre', distance: 5.2, services: ['General Consultation', 'Basic Diagnostics', 'Immunization'], doctorsAvailable: 2, waitingTime: 12, diagnostics: ['Blood Test', 'Urine Test'], medicines: 'Low Stock', emergency: false, beds: 5, occupancy: 40, lat: 26.5000, lng: 91.9000 },
  { id: 'F005', name: 'Specialist Centre Tezpur', type: 'Specialist Centre', distance: 15.3, services: ['Cardiology', 'Neurology', 'Orthopedics', 'Advanced Diagnostics'], doctorsAvailable: 10, waitingTime: 38, diagnostics: ['Echo Cardiogram', 'EEG', 'X-Ray', 'CT Scan'], medicines: 'Available', emergency: false, beds: 50, occupancy: 68, lat: 26.6500, lng: 92.6800 },
];

export const appointments = [
  { id: 'A001', patientId: 'P001', patientName: 'Rahul Sharma', doctorId: 'D001', doctorName: 'Dr. Ananya Sharma', speciality: 'General Physician', facility: 'PHC Chandrapur', date: '2026-08-31', time: '11:30 AM', type: 'Video Consultation', status: 'upcoming', priority: 'normal' },
  { id: 'A002', patientId: 'P002', patientName: 'Ananya Das', doctorId: 'D005', doctorName: 'Dr. Sunita Reddy', speciality: 'Gynecologist', facility: 'PHC Chandrapur', date: '2026-08-31', time: '02:00 PM', type: 'In-Person', status: 'upcoming', priority: 'high' },
  { id: 'A003', patientId: 'P003', patientName: 'Priya Devi', doctorId: 'D002', doctorName: 'Dr. Arjun Das', speciality: 'Cardiologist', facility: 'District Hospital Guwahati', date: '2026-08-30', time: '10:00 AM', type: 'Video Consultation', status: 'completed', priority: 'high' },
  { id: 'A004', patientId: 'P004', patientName: 'Amit Kumar', doctorId: 'D004', doctorName: 'Dr. Ramesh Gupta', speciality: 'Orthopedic', facility: 'District Hospital Guwahati', date: '2026-08-29', time: '03:30 PM', type: 'In-Person', status: 'completed', priority: 'normal' },
  { id: 'A005', patientId: 'P005', patientName: 'Rakesh Singh', doctorId: 'D003', doctorName: 'Dr. Priya Singh', speciality: 'Pediatrician', facility: 'CHC Sonapur', date: '2026-09-01', time: '09:00 AM', type: 'In-Person', status: 'upcoming', priority: 'normal' },
  { id: 'A006', patientId: 'P006', patientName: 'Sunita Boro', doctorId: 'D001', doctorName: 'Dr. Ananya Sharma', speciality: 'General Physician', facility: 'PHC Chandrapur', date: '2026-09-02', time: '11:00 AM', type: 'Video Consultation', status: 'upcoming', priority: 'normal' },
];

export const referrals = [
  { id: 'R001', patientId: 'P001', patientName: 'Rahul Sharma', sourceFacility: 'PHC Chandrapur', destinationFacility: 'District Hospital Guwahati', reason: 'Cardiac evaluation — elevated blood pressure', priority: 'high', status: 'accepted', createdDate: '2026-08-28', expectedDate: '2026-09-02', assignedDoctor: 'Dr. Arjun Das', notes: 'Patient requires ECG and echocardiogram' },
  { id: 'R002', patientId: 'P002', patientName: 'Ananya Das', sourceFacility: 'PHC Chandrapur', destinationFacility: 'CHC Sonapur', reason: 'Prenatal checkup referral', priority: 'high', status: 'completed', createdDate: '2026-08-20', expectedDate: '2026-08-25', assignedDoctor: 'Dr. Sunita Reddy', notes: 'Regular prenatal follow-up' },
  { id: 'R003', patientId: 'P003', patientName: 'Priya Devi', sourceFacility: 'RHC Dhekiajuli', destinationFacility: 'PHC Chandrapur', reason: 'Chronic diabetes management', priority: 'medium', status: 'pending', createdDate: '2026-08-29', expectedDate: '2026-09-05', assignedDoctor: 'Dr. Ananya Sharma', notes: 'HbA1c monitoring required' },
  { id: 'R004', patientId: 'P004', patientName: 'Amit Kumar', sourceFacility: 'PHC Chandrapur', destinationFacility: 'Specialist Centre Tezpur', reason: 'Knee pain — possible meniscus tear', priority: 'medium', status: 'in_transit', createdDate: '2026-08-27', expectedDate: '2026-09-03', assignedDoctor: 'Dr. Ramesh Gupta', notes: 'X-ray results pending review' },
  { id: 'R005', patientId: 'P007', patientName: 'Dipak Gogoi', sourceFacility: 'District Hospital Guwahati', destinationFacility: 'PHC Chandrapur', reason: 'Post-surgery follow-up', priority: 'low', status: 'followup_required', createdDate: '2026-08-15', expectedDate: '2026-09-10', assignedDoctor: 'Dr. Ananya Sharma', notes: 'Hip replacement recovery monitoring' },
  { id: 'R006', patientId: 'P005', patientName: 'Rakesh Singh', sourceFacility: 'CHC Sonapur', destinationFacility: 'District Hospital Guwahati', reason: 'Blood work — iron deficiency', priority: 'medium', status: 'appointment_scheduled', createdDate: '2026-08-25', expectedDate: '2026-09-01', assignedDoctor: 'Dr. Arjun Das', notes: 'CBC and iron studies needed' },
];

export const healthRecords = {
  patient: patients[0],
  timeline: [
    { date: '2026-08-01', event: 'Registration', facility: 'PHC Chandrapur', type: 'registration', details: 'Initial registration with healthcare worker' },
    { date: '2026-08-05', event: 'Health Intake Assessment', facility: 'PHC Chandrapur', type: 'assessment', details: 'Complete health intake questionnaire completed' },
    { date: '2026-08-12', event: 'PHC Consultation', facility: 'PHC Chandrapur', type: 'consultation', details: 'General checkup — Dr. Ananya Sharma' },
    { date: '2026-08-18', event: 'Blood Test', facility: 'PHC Chandrapur', type: 'diagnostic', details: 'CBC, Lipid Profile, Blood Sugar' },
    { date: '2026-08-21', event: 'Specialist Referral', facility: 'PHC → District Hospital', type: 'referral', details: 'Cardiac referral — Dr. Arjun Das' },
    { date: '2026-08-28', event: 'Specialist Consultation', facility: 'District Hospital Guwahati', type: 'consultation', details: 'ECG and blood pressure evaluation' },
    { date: '2026-08-31', event: 'Follow-up Consultation', facility: 'PHC Chandrapur', type: 'followup', details: 'Video follow-up with Dr. Ananya Sharma' },
  ],
  conditions: [
    { name: 'Hypertension', diagnosedDate: '2026-08-12', status: 'Under Management', severity: 'moderate' },
    { name: 'Mild Anemia', diagnosedDate: '2026-08-18', status: 'Improving', severity: 'mild' },
  ],
  prescriptions: [
    { date: '2026-08-28', doctor: 'Dr. Arjun Das', medicines: ['Amlodipine 5mg — Once daily', 'Aspirin 75mg — Once daily'], notes: 'Follow up in 2 weeks' },
    { date: '2026-08-12', doctor: 'Dr. Ananya Sharma', medicines: ['Iron Supplement — Twice daily', 'Folic Acid — Once daily'], notes: 'Recheck blood levels in 4 weeks' },
  ],
  diagnostics: [
    { date: '2026-08-18', test: 'Complete Blood Count', facility: 'PHC Chandrapur', status: 'Available', results: 'Hemoglobin: 10.2 g/dL (Low)', downloadUrl: '#' },
    { date: '2026-08-28', test: 'ECG', facility: 'District Hospital Guwahati', status: 'Available', results: 'Sinus rhythm — No acute abnormalities', downloadUrl: '#' },
  ],
  vaccinations: [
    { name: 'COVID-19 Booster', date: '2026-03-15', status: 'Completed' },
    { name: 'Tetanus', date: '2025-08-20', status: 'Completed' },
  ],
  allergies: ['Penicillin', 'Sulfa drugs'],
};

/** Set by My Patients → Send Message; DoctorMessages reads and clears it. */
export const messageHandoff = { patientId: '' as string };

/* Per-patient clinical records — the doctor's records modal looks these up by
   patient id so every chart reads like a different person's history. */
export interface PatientHealthRecord {
  timeline: { date: string; event: string; facility: string; type: string; details: string }[];
  conditions: { name: string; diagnosedDate: string; status: string; severity: string }[];
  prescriptions: { date: string; doctor: string; medicines: string[]; notes: string }[];
  diagnostics: { date: string; test: string; facility: string; status: string; results: string }[];
  vaccinations: { name: string; date: string; status: string }[];
  allergies: string[];
}

export const patientHealthRecords: Record<string, PatientHealthRecord> = {
  P001: healthRecords,

  P002: {
    timeline: [
      { date: '2026-06-10', event: 'Pregnancy Registration', facility: 'PHC Chandrapur', type: 'registration', details: 'ANC register entry — LMP confirmed, EDD Feb 2027' },
      { date: '2026-07-08', event: 'First ANC Visit', facility: 'PHC Chandrapur', type: 'assessment', details: 'Baseline vitals, blood group, hemoglobin screening' },
      { date: '2026-08-05', event: 'Second ANC Visit', facility: 'PHC Chandrapur', type: 'consultation', details: 'Month 6 checkup — fetal heartbeat normal, BP 112/74' },
      { date: '2026-08-25', event: 'Prenatal Referral Completed', facility: 'CHC Sonapur', type: 'referral', details: 'Gynecology review — Dr. Sunita Reddy, no complications' },
    ],
    conditions: [
      { name: 'Mild Anemia (Pregnancy)', diagnosedDate: '2026-07-08', status: 'Improving', severity: 'mild' },
    ],
    prescriptions: [
      { date: '2026-08-05', doctor: 'Dr. Sunita Reddy', medicines: ['Iron + Folic Acid — Once daily', 'Calcium 500mg — Twice daily'], notes: 'Continue till delivery; review at next ANC' },
    ],
    diagnostics: [
      { date: '2026-07-08', test: 'Hemoglobin Screening', facility: 'PHC Chandrapur', status: 'Available', results: 'Hemoglobin: 10.8 g/dL (Low — improving)' },
      { date: '2026-08-25', test: 'Obstetric Ultrasound', facility: 'CHC Sonapur', status: 'Available', results: 'Single live fetus, growth appropriate for gestational age' },
    ],
    vaccinations: [
      { name: 'Tetanus (Td-2)', date: '2026-07-20', status: 'Completed' },
    ],
    allergies: ['Sulfa drugs'],
  },

  P003: {
    timeline: [
      { date: '2026-03-14', event: 'Diabetes Diagnosis', facility: 'RHC Dhekiajuli', type: 'diagnostic', details: 'Fasting glucose 168 mg/dL — Type 2 Diabetes confirmed' },
      { date: '2026-05-02', event: 'Medication Started', facility: 'PHC Chandrapur', type: 'consultation', details: 'Metformin initiated — lifestyle counselling given' },
      { date: '2026-07-18', event: 'Retinal Screening', facility: 'PHC Chandrapur', type: 'diagnostic', details: 'No diabetic retinopathy changes on fundoscopy' },
      { date: '2026-08-29', event: 'HbA1c Review', facility: 'PHC Chandrapur', type: 'diagnostic', details: 'HbA1c 7.8% — down from 9.1% in March' },
    ],
    conditions: [
      { name: 'Type 2 Diabetes', diagnosedDate: '2026-03-14', status: 'Under Management', severity: 'moderate' },
      { name: 'Hypertension', diagnosedDate: '2026-05-02', status: 'Under Management', severity: 'mild' },
    ],
    prescriptions: [
      { date: '2026-08-29', doctor: 'Dr. Ananya Sharma', medicines: ['Metformin 500mg — Twice daily', 'Amlodipine 2.5mg — Once daily'], notes: 'Continue; repeat HbA1c in 3 months' },
      { date: '2026-05-02', doctor: 'Dr. Ananya Sharma', medicines: ['Metformin 500mg — Twice daily'], notes: 'Start low dose; take with meals' },
    ],
    diagnostics: [
      { date: '2026-08-29', test: 'HbA1c', facility: 'PHC Chandrapur', status: 'Available', results: '7.8% (improved from 9.1%)' },
      { date: '2026-08-29', test: 'Fasting Blood Sugar', facility: 'PHC Chandrapur', status: 'Available', results: '132 mg/dL' },
      { date: '2026-07-18', test: 'Urinary Albumin:Creatinine', facility: 'PHC Chandrapur', status: 'Available', results: 'Within normal limits — no early nephropathy' },
      { date: '2026-03-14', test: 'Lipid Profile', facility: 'RHC Dhekiajuli', status: 'Available', results: 'LDL 128 mg/dL (borderline high)' },
    ],
    vaccinations: [
      { name: 'Influenza', date: '2026-01-10', status: 'Completed' },
      { name: 'Hepatitis B Booster', date: '2022-05-30', status: 'Completed' },
    ],
    allergies: [],
  },

  P004: {
    timeline: [
      { date: '2026-08-10', event: 'Knee Injury Presentation', facility: 'PHC Chandrapur', type: 'consultation', details: 'Right knee pain after fall — suspected meniscus tear' },
      { date: '2026-08-27', event: 'X-Ray & Ortho Review', facility: 'District Hospital Guwahati', type: 'diagnostic', details: 'Imaging done — referred to Dr. Ramesh Gupta' },
    ],
    conditions: [
      { name: 'Right Knee Meniscus Injury', diagnosedDate: '2026-08-10', status: 'Awaiting Review', severity: 'moderate' },
    ],
    prescriptions: [
      { date: '2026-08-10', doctor: 'Dr. Ananya Sharma', medicines: ['Ibuprofen 400mg — As needed', 'Topical diclofenac gel'], notes: 'RICE protocol; orthopedic referral placed' },
    ],
    diagnostics: [
      { date: '2026-08-27', test: 'Knee X-Ray', facility: 'District Hospital Guwahati', status: 'Available', results: 'No fracture; joint space preserved — MRI advised' },
    ],
    vaccinations: [
      { name: 'Tetanus', date: '2024-11-02', status: 'Completed' },
    ],
    allergies: ['Aspirin'],
  },

  P005: {
    timeline: [
      { date: '2026-05-12', event: 'School Health Camp', facility: 'CHC Sonapur', type: 'assessment', details: 'Baseline screening — mild pallor noted, no acute complaints' },
      { date: '2026-08-15', event: 'Fatigue Presentation', facility: 'CHC Sonapur', type: 'consultation', details: 'Pallor and fatigue — iron deficiency suspected' },
      { date: '2026-08-22', event: 'Follow-up Review', facility: 'CHC Sonapur', type: 'followup', details: 'Symptoms unchanged — adherence to iron therapy confirmed' },
      { date: '2026-09-01', event: 'Blood Work Scheduled', facility: 'District Hospital Guwahati', type: 'diagnostic', details: 'CBC and iron studies — appointment booked' },
    ],
    conditions: [
      { name: 'Iron Deficiency Anemia', diagnosedDate: '2026-08-15', status: 'Under Investigation', severity: 'mild' },
      { name: 'Seasonal Allergic Rhinitis', diagnosedDate: '2025-06-02', status: 'Intermittent', severity: 'mild' },
    ],
    prescriptions: [
      { date: '2026-08-22', doctor: 'Dr. Arjun Das', medicines: ['Cetirizine 10mg — At night (as needed)'], notes: 'Only during high pollen weeks' },
      { date: '2026-08-15', doctor: 'Dr. Priya Singh', medicines: ['Ferrous Sulfate 200mg — Once daily', 'Vitamin C 500mg — Once daily'], notes: 'Recheck hemoglobin after 4 weeks' },
    ],
    diagnostics: [
      { date: '2026-08-16', test: 'Peripheral Smear', facility: 'CHC Sonapur', status: 'Available', results: 'Microcytic hypochromic RBCs — consistent with iron deficiency' },
      { date: '2026-08-22', test: 'Serum Ferritin', facility: 'CHC Sonapur', status: 'Available', results: '18 ng/mL (low — stores depleted)' },
    ],
    vaccinations: [
      { name: 'COVID-19 Precaution Dose', date: '2025-11-12', status: 'Completed' },
      { name: 'Tetanus (Td)', date: '2023-04-18', status: 'Completed' },
    ],
    allergies: ['Dust mites'],
  },

  P006: {
    timeline: [
      { date: '2026-06-20', event: 'Thyroid Screening', facility: 'PHC Chandrapur', type: 'diagnostic', details: 'TSH elevated — hypothyroidism detected' },
      { date: '2026-08-28', event: 'Video Follow-up', facility: 'PHC Chandrapur', type: 'followup', details: 'Symptoms improved — TSH reviewed by Dr. Ananya Sharma' },
    ],
    conditions: [
      { name: 'Hypothyroidism', diagnosedDate: '2026-06-20', status: 'Under Management', severity: 'mild' },
    ],
    prescriptions: [
      { date: '2026-06-25', doctor: 'Dr. Ananya Sharma', medicines: ['Levothyroxine 25mcg — Once daily (empty stomach)'], notes: 'TSH recheck every 8 weeks' },
    ],
    diagnostics: [
      { date: '2026-08-28', test: 'TSH', facility: 'PHC Chandrapur', status: 'Available', results: '4.2 mIU/L (improving, near normal range)' },
    ],
    vaccinations: [],
    allergies: [],
  },

  P007: {
    timeline: [
      { date: '2026-07-30', event: 'Hip Replacement Surgery', facility: 'District Hospital Guwahati', type: 'consultation', details: 'Total hip arthroplasty — surgery uneventful' },
      { date: '2026-08-15', event: 'Discharge Review', facility: 'District Hospital Guwahati', type: 'consultation', details: 'Wound healing well — physiotherapy plan issued' },
      { date: '2026-08-29', event: 'Missed Follow-up', facility: 'PHC Chandrapur', type: 'followup', details: 'Did not attend scheduled follow-up — field worker alerted' },
    ],
    conditions: [
      { name: 'Post Hip Replacement Recovery', diagnosedDate: '2026-07-30', status: 'Recovering', severity: 'moderate' },
      { name: 'Osteoarthritis', diagnosedDate: '2024-06-11', status: 'Chronic', severity: 'moderate' },
    ],
    prescriptions: [
      { date: '2026-08-15', doctor: 'Dr. Ramesh Gupta', medicines: ['Paracetamol 650mg — As needed', 'Calcium + Vitamin D3 — Once daily'], notes: 'Physiotherapy twice daily; avoid weight bearing on left side' },
    ],
    diagnostics: [
      { date: '2026-08-15', test: 'Hip X-Ray (Post-Op)', facility: 'District Hospital Guwahati', status: 'Available', results: 'Prosthesis well positioned — no loosening' },
    ],
    vaccinations: [
      { name: 'Influenza', date: '2025-10-05', status: 'Completed' },
    ],
    allergies: ['Latex'],
  },

  P008: {
    timeline: [
      { date: '2025-11-02', event: 'Childhood Immunization Complete', facility: 'PHC Chandrapur', type: 'registration', details: 'Primary immunization series completed as recorded in local register' },
      { date: '2026-08-18', event: 'New Registration', facility: 'PHC Chandrapur', type: 'registration', details: 'Registered by field worker — baseline intake completed' },
      { date: '2026-08-22', event: 'Baseline Health Check', facility: 'PHC Chandrapur', type: 'assessment', details: 'Vitals normal, no chronic conditions reported' },
      { date: '2026-08-30', event: 'Counselling Session', facility: 'PHC Chandrapur', type: 'consultation', details: 'Nutrition and physical activity counselling — health worker Meena' },
    ],
    conditions: [
      { name: 'No Chronic Conditions', diagnosedDate: '2026-08-22', status: 'Healthy', severity: 'none' },
    ],
    prescriptions: [
      { date: '2026-08-22', doctor: 'Dr. Ananya Sharma', medicines: ['Multivitamin — Once daily'], notes: 'General wellness; review at next annual check' },
    ],
    diagnostics: [
      { date: '2026-08-22', test: 'Baseline Vitals Panel', facility: 'PHC Chandrapur', status: 'Available', results: 'BP 108/70, pulse 78, SpO2 99%' },
      { date: '2026-08-22', test: 'Hemoglobin', facility: 'PHC Chandrapur', status: 'Available', results: '13.1 g/dL (normal)' },
    ],
    vaccinations: [
      { name: 'COVID-19 Precaution Dose', date: '2025-12-08', status: 'Completed' },
      { name: 'Tetanus (Td)', date: '2024-09-14', status: 'Completed' },
      { name: 'Hepatitis B Booster', date: '2023-02-20', status: 'Completed' },
    ],
    allergies: [],
  },
};

export const followups = [
  { id: 'FU001', patientId: 'P001', patientName: 'Rahul Sharma', condition: 'Hypertension — Blood Pressure Review', lastConsultation: '2026-08-28', nextFollowup: '2026-09-03', assignedDoctor: 'Dr. Ananya Sharma', priority: 'high', status: 'upcoming', completionRate: 75 },
  { id: 'FU002', patientId: 'P002', patientName: 'Ananya Das', condition: 'Prenatal — Month 7 Checkup', lastConsultation: '2026-08-25', nextFollowup: '2026-09-08', assignedDoctor: 'Dr. Sunita Reddy', priority: 'high', status: 'upcoming', completionRate: 100 },
  { id: 'FU003', patientId: 'P003', patientName: 'Priya Devi', condition: 'Diabetes — HbA1c Monitoring', lastConsultation: '2026-08-20', nextFollowup: '2026-08-28', assignedDoctor: 'Dr. Ananya Sharma', priority: 'high', status: 'missed', completionRate: 50 },
  { id: 'FU004', patientId: 'P007', patientName: 'Dipak Gogoi', condition: 'Post-Surgery Recovery', lastConsultation: '2026-08-15', nextFollowup: '2026-09-10', assignedDoctor: 'Dr. Ramesh Gupta', priority: 'medium', status: 'upcoming', completionRate: 60 },
  { id: 'FU005', patientId: 'P005', patientName: 'Rakesh Singh', condition: 'Iron Deficiency — Blood Test', lastConsultation: '2026-08-22', nextFollowup: '2026-09-05', assignedDoctor: 'Dr. Arjun Das', priority: 'medium', status: 'upcoming', completionRate: 80 },
  { id: 'FU006', patientId: 'P006', patientName: 'Sunita Boro', condition: 'Thyroid — TSH Monitoring', lastConsultation: '2026-08-10', nextFollowup: '2026-08-25', assignedDoctor: 'Dr. Ananya Sharma', priority: 'low', status: 'completed', completionRate: 100 },
];

export const diagnostics = [
  { id: 'DG001', test: 'Complete Blood Count', facility: 'PHC Chandrapur', availability: 'Available', waitingTime: '30 min', distance: 2.4, price: '₹250', category: 'Blood Test' },
  { id: 'DG002', test: 'Lipid Profile', facility: 'PHC Chandrapur', availability: 'Available', waitingTime: '45 min', distance: 2.4, price: '₹400', category: 'Blood Test' },
  { id: 'DG003', test: 'Blood Sugar (Fasting)', facility: 'PHC Chandrapur', availability: 'Available', waitingTime: '20 min', distance: 2.4, price: '₹150', category: 'Blood Test' },
  { id: 'DG004', test: 'X-Ray Chest', facility: 'CHC Sonapur', availability: 'Available', waitingTime: '60 min', distance: 8.1, price: '₹500', category: 'X-Ray' },
  { id: 'DG005', test: 'ECG', facility: 'District Hospital Guwahati', availability: 'Available', waitingTime: '25 min', distance: 22.5, price: '₹300', category: 'ECG' },
  { id: 'DG006', test: 'Ultrasound Abdomen', facility: 'CHC Sonapur', availability: 'Low Slot', waitingTime: '90 min', distance: 8.1, price: '₹800', category: 'Ultrasound' },
  { id: 'DG007', test: 'HbA1c', facility: 'District Hospital Guwahati', availability: 'Available', waitingTime: '40 min', distance: 22.5, price: '₹600', category: 'Blood Test' },
  { id: 'DG008', test: 'CT Scan', facility: 'District Hospital Guwahati', availability: 'Unavailable', waitingTime: '—', distance: 22.5, price: '₹2500', category: 'Imaging' },
  { id: 'DG009', test: 'Thyroid Profile', facility: 'PHC Chandrapur', availability: 'Available', waitingTime: '35 min', distance: 2.4, price: '₹450', category: 'Blood Test' },
  { id: 'DG010', test: 'Urine Routine', facility: 'PHC Chandrapur', availability: 'Available', waitingTime: '15 min', distance: 2.4, price: '₹100', category: 'Pathology' },
];

export const medicines = [
  { id: 'M001', name: 'Amlodipine 5mg', category: 'Chronic Care', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-30', distance: 2.4, manufacturer: 'Cipla' },
  { id: 'M002', name: 'Metformin 500mg', category: 'Chronic Care', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-30', distance: 2.4, manufacturer: 'Sun Pharma' },
  { id: 'M003', name: 'Iron Supplement', category: 'Essential Medicines', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-29', distance: 2.4, manufacturer: 'Zydus' },
  { id: 'M004', name: 'Paracetamol 500mg', category: 'Essential Medicines', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-31', distance: 2.4, manufacturer: 'Dr. Reddy\'s' },
  { id: 'M005', name: 'ORS Sachets', category: 'Essential Medicines', facility: 'CHC Sonapur', stock: 'Low Stock', lastUpdated: '2026-08-28', distance: 8.1, manufacturer: 'Abbot' },
  { id: 'M006', name: 'Iron Folic Acid', category: 'Maternal Care', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-30', distance: 2.4, manufacturer: 'FDC Ltd' },
  { id: 'M007', name: 'Amoxicillin 500mg', category: 'Essential Medicines', facility: 'District Hospital Guwahati', stock: 'Available', lastUpdated: '2026-08-31', distance: 22.5, manufacturer: 'Cipla' },
  { id: 'M008', name: 'Aspirin 75mg', category: 'Chronic Care', facility: 'PHC Chandrapur', stock: 'Available', lastUpdated: '2026-08-30', distance: 2.4, manufacturer: 'Bayer' },
  { id: 'M009', name: 'Vitamin D3', category: 'Essential Medicines', facility: 'CHC Sonapur', stock: 'Low Stock', lastUpdated: '2026-08-27', distance: 8.1, manufacturer: 'Glenmark' },
  { id: 'M010', name: 'Salbutamol Inhaler', category: 'Emergency', facility: 'District Hospital Guwahati', stock: 'Available', lastUpdated: '2026-08-31', distance: 22.5, manufacturer: 'Cipla' },
  { id: 'M011', name: 'Calcium supplements', category: 'Maternal Care', facility: 'PHC Chandrapur', stock: 'Unavailable', lastUpdated: '2026-08-20', distance: 2.4, manufacturer: 'Alkem' },
  { id: 'M012', name: 'ORS + Zinc', category: 'Child Care', facility: 'CHC Sonapur', stock: 'Available', lastUpdated: '2026-08-30', distance: 8.1, manufacturer: 'FDC Ltd' },
];

export const notifications = [
  { id: 'N001', title: 'Referral Accepted', message: 'Dr. Arjun Das has accepted the referral for Rahul Sharma', time: '10 minutes ago', type: 'referral', read: false },
  { id: 'N002', title: 'Consultation Ready', message: 'Dr. Ananya Sharma is ready for your video consultation at 11:30 AM', time: '25 minutes ago', type: 'consultation', read: false },
  { id: 'N003', title: 'Follow-up Reminder', message: 'Your blood pressure review follow-up is due in 3 days', time: '1 hour ago', type: 'followup', read: false },
  { id: 'N004', title: 'Diagnostic Report', message: 'Your ECG results from District Hospital are now available', time: '3 hours ago', type: 'diagnostic', read: true },
  { id: 'N005', title: 'Medicine Update', message: 'Iron supplements are now available at PHC Chandrapur', time: '5 hours ago', type: 'medicine', read: true },
  { id: 'N006', title: 'Appointment Confirmed', message: 'Your appointment with Dr. Priya Singh is confirmed for Sept 1', time: '1 day ago', type: 'appointment', read: true },
];

export const doctorNotifications = [
  { id: 'DN001', title: 'New Patient Referral', message: 'Rahul Sharma has been referred to you for cardiac evaluation', time: '5 minutes ago', type: 'referral', read: false },
  { id: 'DN002', title: 'Appointment Reminder', message: 'Video consultation with Ananya Das at 2:00 PM today', time: '15 minutes ago', type: 'appointment', read: false },
  { id: 'DN003', title: 'Lab Results Available', message: 'Blood test results for Priya Devi are ready for review', time: '1 hour ago', type: 'diagnostic', read: false },
  { id: 'DN004', title: 'Follow-up Missed', message: 'Dipak Gogoi missed the scheduled follow-up appointment', time: '2 hours ago', type: 'followup', read: true },
  { id: 'DN005', title: 'Message from PHC', message: 'Meena Das sent you a patient update for Rakesh Singh', time: '3 hours ago', type: 'consultation', read: true },
  { id: 'DN006', title: 'Referral Completed', message: 'Ananya Das prenatal referral has been completed successfully', time: '1 day ago', type: 'referral', read: true },
  { id: 'DN007', title: 'Schedule Change', message: 'Your 3:30 PM appointment has been rescheduled to 4:00 PM', time: '1 day ago', type: 'appointment', read: true },
];

export const workerNotifications = [
  { id: 'WN001', title: 'Field Visit Due', message: 'Home visit for Sunita Boro is due today before 4:00 PM', time: '20 minutes ago', type: 'followup', read: false },
  { id: 'WN002', title: 'New Patient Assigned', message: 'Mamta Kumari was registered by the PHC and assigned to you', time: '1 hour ago', type: 'referral', read: false },
  { id: 'WN003', title: 'Sync Complete', message: '18 offline records uploaded successfully', time: '4 hours ago', type: 'appointment', read: true },
  { id: 'WN004', title: 'Medicine Stock', message: 'ORS sachets are low at Rural Health Centre Dhekiajuli', time: '1 day ago', type: 'medicine', read: true },
];

export const facilityNotifications = [
  { id: 'FN001', title: 'Bed Capacity Alert', message: 'Occupancy at PHC Chandrapur has crossed 65%', time: '30 minutes ago', type: 'diagnostic', read: false },
  { id: 'FN002', title: 'Inbound Referral', message: 'CHC Sonapur raised a referral for an orthopedic case', time: '2 hours ago', type: 'referral', read: false },
  { id: 'FN003', title: 'Inventory Low', message: 'Iron supplements will run out in 3 days at current usage', time: '5 hours ago', type: 'medicine', read: true },
  { id: 'FN004', title: 'Staff Roster', message: 'Dr. Priya Singh marked unavailable for tomorrow morning', time: '1 day ago', type: 'appointment', read: true },
];

export const messages = [
  {
    id: 'MSG001',
    contactName: 'Dr. Ananya Sharma',
    contactRoleKey: 'msg.role.physician',
    treatingForKey: 'msg.tf.hypAnemia',
    lastMessageKey: 'msg.pm1.5',
    time: '10:30 AM',
    unread: 2,
    messages: [
      { sender: 'doctor', textKey: 'msg.pm1.0', time: '9:45 AM' },
      { sender: 'patient', textKey: 'msg.pm1.1', time: '9:50 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.2', time: '10:00 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.3', time: '10:05 AM' },
      { sender: 'patient', textKey: 'msg.pm1.4', time: '10:15 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.5', time: '10:30 AM' },
    ],
  },
  {
    id: 'MSG002',
    contactName: 'PHC Chandrapur',
    contactRoleKey: 'msg.role.facility',
    treatingForKey: 'msg.tf.videoBooking',
    lastMessageKey: 'msg.pm2.1',
    time: 'Yesterday',
    unread: 0,
    messages: [
      { sender: 'facility', textKey: 'msg.pm2.0', time: 'Yesterday' },
      { sender: 'facility', textKey: 'msg.pm2.1', time: 'Yesterday' },
    ],
  },
{
    id: 'MSG003',
    contactName: 'Care Coordinator',
    contactNameKey: 'msg.name.coordinator',
    contactRoleKey: 'msg.role.worker',
    treatingForKey: 'msg.tf.cardiologyRef',
    lastMessageKey: 'msg.pm3.1',
    time: '2 days ago',
    unread: 1,
    messages: [
      { sender: 'coordinator', textKey: 'msg.pm3.0', time: '2 days ago' },
      { sender: 'coordinator', textKey: 'msg.pm3.1', time: '2 days ago' },
    ],
  },
];

export const doctorMessages = [
  {
    id: 'DMSG001',
    patientId: 'P001',
    contactName: 'Rahul Sharma',
    contactRoleKey: 'msg.role.patient',
    treatingForKey: 'msg.tf.hypAnemia',
    lastMessageKey: 'msg.pm1.5',
    time: '10:30 AM',
    unread: 2,
    messages: [
      { sender: 'doctor', textKey: 'msg.pm1.0', time: '9:45 AM' },
      { sender: 'patient', textKey: 'msg.pm1.1', time: '9:50 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.2', time: '10:00 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.3', time: '10:05 AM' },
      { sender: 'patient', textKey: 'msg.pm1.4', time: '10:15 AM' },
      { sender: 'doctor', textKey: 'msg.pm1.5', time: '10:30 AM' },
    ],
  },
  {
    id: 'DMSG002',
    patientId: 'P003',
    contactName: 'Priya Devi',
    contactRoleKey: 'msg.role.patient',
    treatingForKey: 'msg.tf.diabetes',
    lastMessageKey: 'msg.dm2.4',
    time: 'Yesterday',
    unread: 1,
    messages: [
      { sender: 'doctor', textKey: 'msg.dm2.0', time: '4:10 PM' },
      { sender: 'patient', textKey: 'msg.dm2.1', time: '4:18 PM' },
      { sender: 'doctor', textKey: 'msg.dm2.2', time: '4:22 PM' },
      { sender: 'patient', textKey: 'msg.dm2.3', time: '4:25 PM' },
      { sender: 'doctor', textKey: 'msg.dm2.4', time: '4:30 PM' },
    ],
  },
  {
    id: 'DMSG003',
    patientId: 'P006',
    contactName: 'Sunita Boro',
    contactRoleKey: 'msg.role.patient',
    treatingForKey: 'msg.tf.thyroid',
    lastMessageKey: 'msg.dm3.2',
    time: '2 days ago',
    unread: 0,
    messages: [
      { sender: 'doctor', textKey: 'msg.dm3.0', time: '11:05 AM' },
      { sender: 'patient', textKey: 'msg.dm3.1', time: '11:12 AM' },
      { sender: 'doctor', textKey: 'msg.dm3.2', time: '11:15 AM' },
    ],
  },
];

export const analyticsData = {
  patientFlow: [
    { month: 'Apr', registrations: 120, consultations: 95, referrals: 32 },
    { month: 'May', registrations: 145, consultations: 120, referrals: 38 },
    { month: 'Jun', registrations: 132, consultations: 110, referrals: 35 },
    { month: 'Jul', registrations: 168, consultations: 142, referrals: 45 },
    { month: 'Aug', registrations: 195, consultations: 165, referrals: 52 },
  ],
  referralCompletion: [
    { month: 'Apr', completed: 28, pending: 4, rate: 87 },
    { month: 'May', completed: 33, pending: 5, rate: 87 },
    { month: 'Jun', completed: 30, pending: 5, rate: 86 },
    { month: 'Jul', completed: 40, pending: 5, rate: 89 },
    { month: 'Aug', completed: 46, pending: 6, rate: 88 },
  ],
  waitingTime: [
    { facility: 'PHC Chandrapur', avgTime: 18 },
    { facility: 'CHC Sonapur', avgTime: 32 },
    { facility: 'District Hospital', avgTime: 45 },
    { facility: 'RHC Dhekiajuli', avgTime: 12 },
    { facility: 'Specialist Centre', avgTime: 38 },
  ],
  facilityLoad: [
    { name: 'PHC Chandrapur', occupancy: 65, capacity: 100 },
    { name: 'CHC Sonapur', occupancy: 72, capacity: 100 },
    { name: 'District Hospital', occupancy: 81, capacity: 100 },
    { name: 'RHC Dhekiajuli', occupancy: 40, capacity: 100 },
    { name: 'Specialist Centre', occupancy: 68, capacity: 100 },
  ],
  followupCompletion: [
    { month: 'Apr', completed: 85, missed: 15 },
    { month: 'May', completed: 88, missed: 12 },
    { month: 'Jun', completed: 82, missed: 18 },
    { month: 'Jul', completed: 90, missed: 10 },
    { month: 'Aug', completed: 87, missed: 13 },
  ],
  kpis: {
    avgTravelDistanceAvoided: '14.2 km',
    avgWaitingTime: '28 min',
    referralCompletionRate: '88%',
    referralTurnaround: '3.2 days',
    followupCompletionRate: '87%',
    diagnosticAvailability: '78%',
    medicineAvailability: '82%',
  },
};

export const healthcareWorkers = [
  { id: 'HW001', name: 'Meena Das', role: 'ASHA Worker', facility: 'PHC Chandrapur', area: 'Chandrapur Village', patientsRegistered: 48, referralsCreated: 12, followupsCompleted: 35, phone: '+91 98760 20001' },
  { id: 'HW002', name: 'Rina Boro', role: 'ANM', facility: 'CHC Sonapur', area: 'Sonapur Block', patientsRegistered: 62, referralsCreated: 18, followupsCompleted: 48, phone: '+91 98760 20002' },
];

export const facilityStats = {
  patientLoad: { today: 45, thisWeek: 280, thisMonth: 1120 },
  avgWaitingTime: 28,
  pendingReferrals: 8,
  followupGaps: 5,
  availableDoctors: 3,
  diagnosticCapacity: 72,
  medicineStockLevel: 82,
};
