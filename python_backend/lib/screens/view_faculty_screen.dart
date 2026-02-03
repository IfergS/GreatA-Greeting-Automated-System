import 'package:flutter/material.dart';
import '../models/faculty.dart';
import '../services/storage_service.dart';
import '../utils/app_theme.dart';

class ViewFacultyScreen extends StatelessWidget {
  const ViewFacultyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final storageService = StorageService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('👥 View Faculty'),
      ),
      body: FutureBuilder<List<Faculty>>(
        future: storageService.getAllFaculty(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(
              child: Text(
                'No faculty members registered yet',
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            );
          }

          final facultyList = snapshot.data!;

          return ListView.builder(
            padding: const EdgeInsets.all(20),
            itemCount: facultyList.length,
            itemBuilder: (context, index) {
              final faculty = facultyList[index];
              return Card(
                color: AppTheme.secondaryColor,
                margin: const EdgeInsets.only(bottom: 15),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppTheme.accentColor,
                    radius: 30,
                    child: Text(
                      faculty.name[0].toUpperCase(),
                      style: const TextStyle(
                        color: AppTheme.textPrimary,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  title: Text(
                    faculty.name,
                    style: const TextStyle(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 5),
                      Text(
                        'ID: ${faculty.id}',
                        style: const TextStyle(color: AppTheme.textSecondary),
                      ),
                      if (faculty.email != null && faculty.email!.isNotEmpty)
                        Text(
                          'Email: ${faculty.email}',
                          style: const TextStyle(color: AppTheme.textSecondary),
                        ),
                      if (faculty.phone != null && faculty.phone!.isNotEmpty)
                        Text(
                          'Phone: ${faculty.phone}',
                          style: const TextStyle(color: AppTheme.textSecondary),
                        ),
                    ],
                  ),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () async {
                      final confirm = await showDialog<bool>(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: const Text('Delete Faculty'),
                          content: Text('Are you sure you want to delete ${faculty.name}? This will also delete all training images.'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context, false),
                              child: const Text('Cancel'),
                            ),
                            TextButton(
                              onPressed: () => Navigator.pop(context, true),
                              child: const Text('Delete', style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                      );

                      if (confirm == true) {
                        await storageService.deleteFaculty(faculty.id);
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Faculty deleted successfully')),
                          );
                          Navigator.pop(context, true);
                        }
                      }
                    },
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

